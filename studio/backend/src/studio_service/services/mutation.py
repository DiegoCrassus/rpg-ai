"""S4 proposal builder: allowlist, op→diff, in-memory store (INVES-86)."""

from __future__ import annotations

import difflib
import importlib
import re
import sys
import uuid
from dataclasses import dataclass, field
from studio_service.time_utils import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from studio_service.api.errors import StudioApiError
from studio_service.schemas.proposals import (
    DryRunResult,
    GatewayPathResult,
    ProposalCreateRequest,
    ProposalResponse,
    StructuredOp,
)
from studio_service.services.doctor_runner import run_doctor_in_workspace
from studio_service.services.engine import EngineService
from studio_service.services.proposal_workspace import (
    build_doctor_workspace,
    build_validate_workspace,
    cleanup_workspace,
)

AUTHORITY_BADGE = "proposed_non_authoritative"
PROPOSAL_TTL = timedelta(hours=24)


@dataclass
class StoredProposal:
    proposal_id: str
    request: ProposalCreateRequest
    patch_body: str
    proposed_files: dict[str, str]
    created_at: datetime
    dry_runs: dict[str, DryRunResult] = field(default_factory=dict)


class ProposalStore:
    """In-memory proposal registry with TTL eviction."""

    def __init__(self) -> None:
        self._items: dict[str, StoredProposal] = {}

    def _evict_expired(self) -> None:
        cutoff = datetime.now(UTC) - PROPOSAL_TTL
        expired = [pid for pid, p in self._items.items() if p.created_at < cutoff]
        for pid in expired:
            del self._items[pid]

    def create(self, proposal: StoredProposal) -> StoredProposal:
        self._evict_expired()
        self._items[proposal.proposal_id] = proposal
        return proposal

    def get(self, proposal_id: str) -> StoredProposal | None:
        self._evict_expired()
        return self._items.get(proposal_id)

    def delete(self, proposal_id: str) -> bool:
        self._evict_expired()
        return self._items.pop(proposal_id, None) is not None

    def record_dry_run(self, proposal_id: str, result: DryRunResult) -> None:
        stored = self._items.get(proposal_id)
        if stored is None:
            raise StudioApiError(404, "PROPOSAL_NOT_FOUND", f"Unknown proposal: {proposal_id}")
        stored.dry_runs[result.step] = result


_store = ProposalStore()


def get_proposal_store() -> ProposalStore:
    return _store


def reset_proposal_store_for_tests() -> None:
    """Clear in-memory proposals (tests only)."""

    _store._items.clear()


def _load_studio_policy(repo_root: Path) -> dict[str, Any]:
    path = repo_root / ".sdlc/gateways/policy.yaml"
    if not path.is_file():
        raise StudioApiError(500, "POLICY_MISSING", f"Missing policy file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    block = data.get("studio_proposals")
    if not isinstance(block, dict):
        raise StudioApiError(500, "POLICY_INVALID", "studio_proposals block missing in policy.yaml")
    return block


def _normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        return normalized[2:]
    return normalized


def _matches_prefix(rel_path: str, prefix: str) -> bool:
    if prefix.endswith("/"):
        return rel_path.startswith(prefix) or rel_path == prefix.rstrip("/")
    return rel_path == prefix or rel_path.startswith(prefix + "/")


def _path_allowed(rel_path: str, policy: dict[str, Any]) -> tuple[bool, str]:
    rel = _normalize_path(rel_path)
    for forbidden in policy.get("forbidden_target_prefixes", []):
        if _matches_prefix(rel, forbidden):
            return False, f"forbidden prefix: {forbidden}"
    allowed_prefixes = policy.get("allowed_target_prefixes", [])
    if any(_matches_prefix(rel, p) for p in allowed_prefixes):
        return True, "allowed by studio_proposals allowlist"
    return False, "path_not_allowed"


def _validate_target_paths(paths: list[str], policy: dict[str, Any]) -> None:
    denied: list[dict[str, str]] = []
    for path in paths:
        ok, reason = _path_allowed(path, policy)
        if not ok:
            denied.append({"path": _normalize_path(path), "reason": reason})
    if denied:
        raise StudioApiError(
            422,
            "path_not_allowed",
            "One or more target_paths are outside the Studio allowlist",
            details={"paths": denied},
        )


def _import_gate(repo_root: Path):
    dsl_dir = str((repo_root / ".sdlc/dsl").resolve())
    if dsl_dir not in sys.path:
        sys.path.insert(0, dsl_dir)
    return importlib.import_module("gate")


def _read_repo_file(repo_root: Path, rel_path: str) -> str | None:
    path = repo_root / rel_path
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return None


def _apply_op(repo_root: Path, op: StructuredOp, contents: dict[str, str]) -> None:
    rel = _normalize_path(op.path)
    current = contents.get(rel)
    if current is None:
        current = _read_repo_file(repo_root, rel)

    if op.op == "create_file":
        if op.content is None:
            raise StudioApiError(422, "INVALID_OP", "create_file requires content", details={"path": rel})
        parent = (repo_root / rel).parent
        if not parent.exists():
            raise StudioApiError(422, "INVALID_OP", "Parent directory does not exist", details={"path": rel})
        contents[rel] = op.content
        return

    if op.op == "replace_block":
        if op.content is None:
            raise StudioApiError(422, "INVALID_OP", "replace_block requires content", details={"path": rel})
        contents[rel] = op.content
        return

    if current is None:
        raise StudioApiError(422, "INVALID_OP", "Target file does not exist", details={"path": rel})

    lines = current.splitlines(keepends=True)
    if op.op == "insert_after":
        if op.content is None:
            raise StudioApiError(422, "INVALID_OP", "insert_after requires content", details={"path": rel})
        anchor = op.anchor or ""
        idx = _find_anchor_index(lines, anchor)
        insert = op.content if op.content.endswith("\n") else op.content + "\n"
        lines[idx + 1 : idx + 1] = [insert]
        contents[rel] = "".join(lines)
        return

    if op.op == "delete_lines":
        anchor = op.anchor or ""
        if not anchor:
            raise StudioApiError(422, "INVALID_OP", "delete_lines requires anchor", details={"path": rel})
        pattern = re.compile(anchor)
        contents[rel] = "".join(line for line in lines if not pattern.search(line))
        return

    raise StudioApiError(422, "INVALID_OP", f"Unsupported op: {op.op}")


def _find_anchor_index(lines: list[str], anchor: str) -> int:
    try:
        pattern = re.compile(anchor)
        use_regex = True
    except re.error:
        pattern = None
        use_regex = False
    for idx, line in enumerate(lines):
        if use_regex and pattern and pattern.search(line):
            return idx
        if not use_regex and anchor in line:
            return idx
    raise StudioApiError(422, "ANCHOR_NOT_FOUND", f"Anchor not found: {anchor}")


def _compile_yaml_content(repo_root: Path, rel: str, new_content: str) -> None:
    if not rel.endswith((".yaml", ".yml")):
        return
    try:
        yaml.safe_load(new_content)
    except yaml.YAMLError as exc:
        raise StudioApiError(
            422,
            "INVALID_YAML",
            f"Invalid YAML for {rel}",
            details={"path": rel, "error": str(exc)},
        ) from exc
    existing = _read_repo_file(repo_root, rel)
    if existing is not None:
        try:
            yaml.safe_load(existing)
        except yaml.YAMLError:
            pass


def _build_patch_body(
    repo_root: Path,
    proposed_files: dict[str, str],
) -> str:
    chunks: list[str] = []
    for rel in sorted(proposed_files):
        old = _read_repo_file(repo_root, rel)
        new = proposed_files[rel]
        old_lines = (old or "").splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)
        if old == new:
            continue
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
        )
        chunks.append("".join(diff))
    return "".join(chunks)


def _materialize_proposal(
    repo_root: Path,
    body: ProposalCreateRequest,
) -> tuple[dict[str, str], str]:
    policy = _load_studio_policy(repo_root)
    normalized_targets = [_normalize_path(p) for p in body.target_paths]
    _validate_target_paths(normalized_targets, policy)

    for op in body.ops:
        op_path = _normalize_path(op.path)
        if op_path not in normalized_targets:
            raise StudioApiError(
                422,
                "path_not_allowed",
                "op.path must be listed in target_paths",
                details={"path": op_path},
            )
        ok, reason = _path_allowed(op_path, policy)
        if not ok:
            raise StudioApiError(
                422,
                "path_not_allowed",
                reason,
                details={"path": op_path},
            )

    proposed: dict[str, str] = {}
    for op in body.ops:
        _apply_op(repo_root, op, proposed)

    for rel, content in proposed.items():
        _compile_yaml_content(repo_root, rel, content)

    patch_body = _build_patch_body(repo_root, proposed)
    if not patch_body.strip():
        raise StudioApiError(422, "EMPTY_PROPOSAL", "Proposal produced no diff")

    return proposed, patch_body


def create_proposal(repo_root: Path, body: ProposalCreateRequest) -> ProposalResponse:
    proposed_files, patch_body = _materialize_proposal(repo_root, body)
    proposal_id = str(uuid.uuid4())
    created_at = datetime.now(UTC)
    stored = StoredProposal(
        proposal_id=proposal_id,
        request=body,
        patch_body=patch_body,
        proposed_files=proposed_files,
        created_at=created_at,
    )
    _store.create(stored)
    return _to_response(stored)


def get_proposal(proposal_id: str) -> ProposalResponse:
    stored = _store.get(proposal_id)
    if stored is None:
        raise StudioApiError(404, "PROPOSAL_NOT_FOUND", f"Unknown proposal: {proposal_id}")
    return _to_response(stored)


def delete_proposal(proposal_id: str) -> None:
    if not _store.delete(proposal_id):
        raise StudioApiError(404, "PROPOSAL_NOT_FOUND", f"Unknown proposal: {proposal_id}")


def _to_response(stored: StoredProposal) -> ProposalResponse:
    return ProposalResponse(
        proposal_id=stored.proposal_id,
        kind=stored.request.kind,
        title=stored.request.title,
        target_paths=[_normalize_path(p) for p in stored.request.target_paths],
        patch_body=stored.patch_body,
        simulated_gate=stored.request.simulated_gate,
        created_at=stored.created_at.isoformat(),
        dry_runs=dict(stored.dry_runs),
    )


def _require_stored(proposal_id: str) -> StoredProposal:
    stored = _store.get(proposal_id)
    if stored is None:
        raise StudioApiError(404, "PROPOSAL_NOT_FOUND", f"Unknown proposal: {proposal_id}")
    return stored


def run_validate(repo_root: Path, proposal_id: str, engine: EngineService) -> DryRunResult:
    stored = _require_stored(proposal_id)
    workspace = build_validate_workspace(repo_root, stored.proposed_files)
    try:
        payload = engine.validate(workspace)
        fail_count = int((payload.get("summary") or {}).get("fail", 0))
        if fail_count:
            result = DryRunResult(
                proposal_id=proposal_id,
                step="validate",
                exit_code=1,
                summary=f"Studio validation reported {fail_count} failure(s)",
                details=list(payload.get("results") or [])[:20],
            )
        else:
            result = DryRunResult(
                proposal_id=proposal_id,
                step="validate",
                exit_code=0,
                summary="Studio compile and validate passed on proposed files",
                details=[],
            )
    except StudioApiError as exc:
        result = DryRunResult(
            proposal_id=proposal_id,
            step="validate",
            exit_code=1,
            summary=exc.body["error"]["message"],
            details=[exc.body.get("error", {}).get("details") or {}],
        )
    except Exception as exc:  # noqa: BLE001
        result = DryRunResult(
            proposal_id=proposal_id,
            step="validate",
            exit_code=1,
            summary=str(exc),
            details=[{"error": str(exc)}],
        )
    finally:
        cleanup_workspace(workspace)

    _store.record_dry_run(proposal_id, result)
    return result


def run_doctor(repo_root: Path, proposal_id: str) -> DryRunResult:
    stored = _require_stored(proposal_id)
    workspace = build_doctor_workspace(repo_root, stored.proposed_files)
    try:
        exit_code, summary, details = run_doctor_in_workspace(workspace, repo_root)
        result = DryRunResult(
            proposal_id=proposal_id,
            step="doctor",
            exit_code=0 if exit_code == 0 else 1,
            summary=summary,
            details=details,
        )
    except Exception as exc:  # noqa: BLE001
        result = DryRunResult(
            proposal_id=proposal_id,
            step="doctor",
            exit_code=1,
            summary=f"Doctor run failed: {exc}",
            details=[{"error": str(exc)}],
        )
    finally:
        cleanup_workspace(workspace)

    _store.record_dry_run(proposal_id, result)
    return result


def run_gateway_check(repo_root: Path, proposal_id: str) -> DryRunResult:
    stored = _require_stored(proposal_id)
    gate = _import_gate(repo_root)
    state = gate.load_session_gate(repo_root)
    stage = stored.request.simulated_gate.stage
    path_results: list[GatewayPathResult] = []
    all_allowed = True

    for rel in stored.request.target_paths:
        normalized = _normalize_path(rel)
        allowed, reason = gate.check_write_simulated(normalized, stage, repo_root)
        path_results.append(
            GatewayPathResult(
                path=normalized,
                allowed=allowed,
                reason=reason,
                gate_status=state.gate_status,
                stage=state.stage or stage,
            )
        )
        if not allowed:
            all_allowed = False

    result = DryRunResult(
        proposal_id=proposal_id,
        step="gateway-check",
        exit_code=0 if all_allowed else 1,
        summary="All target paths allowed for simulated gate"
        if all_allowed
        else "One or more target paths denied by gateway check",
        details=[p.model_dump() for p in path_results],
    )
    _store.record_dry_run(proposal_id, result)
    return result

"""Read-only browse of allowlisted `.cursor/` config paths for Studio builders."""

from __future__ import annotations

from pathlib import Path

from studio_service.api.errors import StudioApiError
from studio_service.schemas.config import (
    ConfigFileContentResponse,
    ConfigFileEntry,
    ConfigFileListResponse,
    ConfigKind,
)
from studio_service.services.mutation import _load_studio_policy, _normalize_path, _path_allowed

_KIND_ROOTS: dict[ConfigKind, tuple[str, ...]] = {
    "agent": (".cursor/agents/",),
    "rule": (".cursor/rules/",),
    "skill": (".cursor/skills/",),
    "command": (".cursor/commands/",),
}

_KIND_SUFFIXES: dict[ConfigKind, tuple[str, ...]] = {
    "agent": (".md",),
    "rule": (".mdc",),
    "skill": (".md",),
    "command": (".md",),
}


def _assert_kind(kind: str) -> ConfigKind:
    if kind not in _KIND_ROOTS:
        raise StudioApiError(
            400,
            "INVALID_CONFIG_KIND",
            f"Unknown config kind: {kind}",
            details={"allowed": list(_KIND_ROOTS)},
        )
    return kind  # type: ignore[return-value]


def _assert_readable_path(repo_root: Path, rel_path: str) -> str:
    normalized = _normalize_path(rel_path)
    policy = _load_studio_policy(repo_root)
    ok, reason = _path_allowed(normalized, policy)
    if not ok:
        raise StudioApiError(
            422,
            "path_not_allowed",
            reason,
            details={"path": normalized},
        )
    full = repo_root / normalized
    if full.is_file():
        try:
            full.resolve().relative_to(repo_root.resolve())
        except ValueError as exc:
            raise StudioApiError(400, "INVALID_PATH", "Path escapes repo root") from exc
    return normalized


def _matches_kind(path: str, kind: ConfigKind) -> bool:
    normalized = _normalize_path(path)
    roots = _KIND_ROOTS[kind]
    suffixes = _KIND_SUFFIXES[kind]
    if not any(normalized.startswith(root) for root in roots):
        return False
    if not any(normalized.endswith(suffix) for suffix in suffixes):
        return False
    if kind == "skill" and normalized.endswith("/SKILL.md"):
        return True
    if kind == "skill":
        return "/skills/" in normalized
    return True


def list_config_files(
    repo_root: Path,
    kind: str,
    *,
    q: str | None = None,
) -> ConfigFileListResponse:
    resolved_kind = _assert_kind(kind)
    query = (q or "").strip().lower()
    entries: list[ConfigFileEntry] = []

    for root in _KIND_ROOTS[resolved_kind]:
        base = repo_root / root.rstrip("/")
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            rel = _normalize_path(str(path.relative_to(repo_root)))
            if not _matches_kind(rel, resolved_kind):
                continue
            name = path.name
            haystack = f"{rel} {name}".lower()
            if query and query not in haystack:
                continue
            entries.append(
                ConfigFileEntry(
                    path=rel,
                    name=name,
                    size_bytes=path.stat().st_size,
                )
            )

    return ConfigFileListResponse(kind=resolved_kind, files=entries, q=q or None)


def read_config_file(repo_root: Path, rel_path: str) -> ConfigFileContentResponse:
    normalized = _assert_readable_path(repo_root, rel_path)
    full = repo_root / normalized
    if not full.is_file():
        return ConfigFileContentResponse(path=normalized, content="", exists=False)
    content = full.read_text(encoding="utf-8")
    return ConfigFileContentResponse(path=normalized, content=content, exists=True)

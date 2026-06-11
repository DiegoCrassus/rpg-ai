"""S4 propose-only mutation routes (no /apply)."""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from studio_service.deps import EngineSvc, RepoRoot
from studio_service.schemas.proposals import (
    DryRunResult,
    ProposalCreateRequest,
    ProposalResponse,
)
from studio_service.services.mutation import (
    create_proposal,
    delete_proposal,
    get_proposal,
    run_doctor,
    run_gateway_check,
    run_validate,
)

router = APIRouter(prefix="/proposals", tags=["s4-proposals"])


@router.post("", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
def proposals_create(body: ProposalCreateRequest, repo_root: RepoRoot) -> ProposalResponse:
    return create_proposal(repo_root, body)


@router.get("/{proposal_id}", response_model=ProposalResponse)
def proposals_get(proposal_id: str) -> ProposalResponse:
    return get_proposal(proposal_id)


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
def proposals_delete(proposal_id: str) -> Response:
    delete_proposal(proposal_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{proposal_id}/validate", response_model=DryRunResult)
def proposals_validate(
    proposal_id: str,
    repo_root: RepoRoot,
    engine: EngineSvc,
) -> DryRunResult:
    return run_validate(repo_root, proposal_id, engine)


@router.post("/{proposal_id}/doctor", response_model=DryRunResult)
def proposals_doctor(proposal_id: str, repo_root: RepoRoot) -> DryRunResult:
    return run_doctor(repo_root, proposal_id)


@router.post("/{proposal_id}/gateway-check", response_model=DryRunResult)
def proposals_gateway_check(proposal_id: str, repo_root: RepoRoot) -> DryRunResult:
    return run_gateway_check(repo_root, proposal_id)

"""S5 validation inspect/run, doctor, simulation, assistance, skeleton."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from studio_service.config import Settings, get_settings
from studio_service.deps import RepoRoot, resolve_repo_root
from studio_service.schemas.foundation_views import (
    DoctorRunBody,
    SimulationPreviewBody,
    ValidationRunBody,
    WorkflowAssistanceBody,
)
from studio_service.services.foundation_views import (
    build_simulation_preview,
    build_validation_inspection,
    build_workflow_assistance,
    list_test_skeleton,
    run_repo_doctor,
    run_validation,
)

router = APIRouter(tags=["s5-validation"])


@router.get("/validation/inspect")
def validation_inspect(
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
    root: str | None = Query(default=None),
    status: str | None = Query(default=None),
    check_type: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    group_by: str = Query(default="status"),
) -> dict:
    target = resolve_repo_root(root, settings) if root else repo_root
    return build_validation_inspection(
        target,
        status=status,
        check_type=check_type,
        target_type=target_type,
        group_by=group_by,
    )


@router.post("/validation/run")
def validation_run(
    body: ValidationRunBody,
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    target = resolve_repo_root(body.root, settings) if body.root else repo_root
    return run_validation(target)


@router.post("/doctor/run")
def doctor_run(
    body: DoctorRunBody,
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    target = resolve_repo_root(body.root, settings) if body.root else repo_root
    return run_repo_doctor(target)


@router.post("/simulation/preview")
def simulation_preview(
    body: SimulationPreviewBody,
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    target = resolve_repo_root(body.root, settings) if body.root else repo_root
    return build_simulation_preview(
        target,
        scenario=body.scenario,
        intent=body.intent,
        path_label=body.path_label,
        step_kind=body.step_kind,
        tag=body.tag,
    )


@router.post("/assistance/workflow")
def assistance_workflow(
    body: WorkflowAssistanceBody,
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    target = resolve_repo_root(body.root, settings) if body.root else repo_root
    return build_workflow_assistance(target, kind=body.kind)


@router.get("/skeleton/tests")
def skeleton_tests() -> dict:
    return list_test_skeleton()

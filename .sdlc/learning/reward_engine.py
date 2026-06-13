"""Deterministic reward engine for SDLC task executions."""

from __future__ import annotations

from dataclasses import dataclass

try:
    from .schemas import TaskOutcome
except ImportError:
    from schemas import TaskOutcome  # type: ignore[no-redef]


@dataclass
class RewardInput:
    tests_fail: int = 0
    tests_pass: int | None = None
    lint_exit: int | None = None
    typecheck_exit: int | None = None
    doctor_exit: int | None = None
    security_exit: int | None = None
    rollback: bool = False
    rework_count: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    tools_total: int = 0
    tools_failed: int = 0
    requirement_adherence: float | None = None
    human_approved: bool | None = None
    human_escalated: bool = False
    files_changed: int | None = None
    gateway_block: bool = False
    hallucination: bool = False


class RewardEngine:
    """Rule-based reward in [-1.0, 1.0]. No ML."""

    TOKEN_BUDGET_SOFT = 40_000
    TOKEN_BUDGET_HARD = 120_000
    REWORK_PENALTY_EACH = 0.15
    TOOL_FAIL_PENALTY = 0.05

    def compute(self, data: RewardInput) -> tuple[float, TaskOutcome]:
        if data.rollback:
            return -1.0, TaskOutcome.FAILURE

        if data.security_exit is not None and data.security_exit != 0:
            return -1.0, TaskOutcome.FAILURE

        reward = 0.85
        outcome = TaskOutcome.SUCCESS

        if data.tests_fail > 0:
            reward = min(reward, 0.0)
            outcome = TaskOutcome.FAILURE

        if data.lint_exit is not None and data.lint_exit != 0:
            reward = min(reward, 0.2)
            outcome = TaskOutcome.FAILURE if outcome == TaskOutcome.SUCCESS else outcome

        if data.typecheck_exit is not None and data.typecheck_exit != 0:
            reward = min(reward, 0.2)
            outcome = TaskOutcome.FAILURE if outcome == TaskOutcome.SUCCESS else outcome

        if data.doctor_exit is not None and data.doctor_exit != 0:
            reward -= 0.25
            outcome = TaskOutcome.PARTIAL if outcome == TaskOutcome.SUCCESS else outcome

        if data.gateway_block:
            reward -= 0.3

        if data.hallucination:
            reward -= 0.4
            outcome = TaskOutcome.FAILURE

        reward -= min(0.45, data.rework_count * self.REWORK_PENALTY_EACH)

        if data.tools_failed > 0 and data.tools_total > 0:
            ratio = data.tools_failed / max(data.tools_total, 1)
            reward -= min(0.3, ratio * 0.5)

        total_tokens = data.tokens_in + data.tokens_out
        if total_tokens > self.TOKEN_BUDGET_HARD:
            reward -= 0.25
        elif total_tokens > self.TOKEN_BUDGET_SOFT:
            reward -= 0.1
        elif total_tokens < self.TOKEN_BUDGET_SOFT // 4 and outcome == TaskOutcome.SUCCESS:
            reward += 0.05

        if data.requirement_adherence is not None:
            reward += (data.requirement_adherence - 0.5) * 0.2

        if data.files_changed is not None and data.files_changed > 30:
            reward -= 0.1

        if data.human_approved is True:
            reward += 0.15
        if data.human_escalated:
            reward -= 0.3
            outcome = TaskOutcome.PARTIAL

        reward = max(-1.0, min(1.0, round(reward, 4)))

        if reward <= 0 and outcome == TaskOutcome.SUCCESS and data.tests_fail == 0:
            outcome = TaskOutcome.PARTIAL

        return reward, outcome

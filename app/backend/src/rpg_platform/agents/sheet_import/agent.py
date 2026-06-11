"""Deep Agent integration for sheet import (optional — requires OpenAI)."""

from __future__ import annotations

import uuid

from rpg_platform.agents.sheet_import.runner import default_mock_proposal


async def build_proposal_with_agent(job_id: uuid.UUID) -> dict:
    """Placeholder for create_deep_agent integration.

    Real agent wiring uses deepagents + langchain-openai when OPENAI_API_KEY is set.
    Falls back to deterministic mock proposal for CI/local without API key.
    """
    # MVP: return mock until vision pipeline is configured with live keys
    return default_mock_proposal(job_id)

"""LangChain and LangGraph based business research agent skeleton."""

from __future__ import annotations

from dataclasses import dataclass

from app.core import get_logger

logger = get_logger({"component": "business-research-agent"})


@dataclass(slots=True)
class AgentTask:
    """Input task for business research agent."""

    objective: str
    business_name: str | None = None
    website: str | None = None


class BusinessResearchAgent:
    """Minimal multi-step reasoning agent scaffold.

    This class is intentionally provider-agnostic and serves as a stable
    extension point for integrating LangChain/LangGraph workflows.
    """

    async def run(self, task: AgentTask) -> dict[str, str]:
        """Execute a basic placeholder research workflow."""
        logger.info("Running research agent objective='{}'", task.objective)

        # Future implementation: tool-enabled LangGraph state machine.
        return {
            "status": "planned",
            "objective": task.objective,
            "business_name": task.business_name or "",
            "website": task.website or "",
            "note": "LangGraph workflow hook ready for advanced reasoning.",
        }

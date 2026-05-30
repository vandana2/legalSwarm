"""
AgentService – thin wrapper kept for backwards compatibility.
Delegates directly to the single orchestration pipeline.
"""

from typing import Dict, Any
from services.crew_orchestrator import run_contract_analysis


class AgentService:
    """Orchestrate AI agents for contract analysis."""

    async def analyze(self, contract_text: str) -> Dict[str, Any]:
        """Run the full six-agent pipeline and return the typed result."""
        return run_contract_analysis(contract_text)


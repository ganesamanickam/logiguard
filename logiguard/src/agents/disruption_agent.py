"""Disruption specialist agent."""

from typing import List
from .base_agent import BaseAgent
from ..config.prompts import DISRUPTION_AGENT_PROMPT
from ..tools.disruption_tools import check_active_disruptions, assess_regional_risk


class DisruptionAgent(BaseAgent):
    """Disruption specialist agent with isolated tool access."""
    
    def __init__(self):
        """Initialize disruption agent."""
        super().__init__(
            name="DisruptionAgent",
            system_prompt=DISRUPTION_AGENT_PROMPT
        )
    
    def get_tools(self) -> List:
        """Get disruption-specific tools.
        
        Returns:
            List of 2 disruption tools
        """
        return [
            check_active_disruptions,
            assess_regional_risk
        ]

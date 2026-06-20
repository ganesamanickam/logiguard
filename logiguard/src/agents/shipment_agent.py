"""Shipment specialist agent."""

from typing import List
from .base_agent import BaseAgent
from ..config.prompts import SHIPMENT_AGENT_PROMPT
from ..tools.shipment_tools import get_shipment_status, calculate_delivery_windows


class ShipmentAgent(BaseAgent):
    """Shipment specialist agent with isolated tool access."""
    
    def __init__(self):
        """Initialize shipment agent."""
        super().__init__(
            name="ShipmentAgent",
            system_prompt=SHIPMENT_AGENT_PROMPT
        )
    
    def get_tools(self) -> List:
        """Get shipment-specific tools.
        
        Returns:
            List of 2 shipment tools
        """
        return [
            get_shipment_status,
            calculate_delivery_windows
        ]

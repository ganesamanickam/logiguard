"""Inventory specialist agent."""

from typing import List
from .base_agent import BaseAgent
from ..config.prompts import INVENTORY_AGENT_PROMPT
from ..tools.inventory_tools import query_inventory_levels, check_safety_stock_violations


class InventoryAgent(BaseAgent):
    """Inventory specialist agent with isolated tool access."""
    
    def __init__(self):
        """Initialize inventory agent."""
        super().__init__(
            name="InventoryAgent",
            system_prompt=INVENTORY_AGENT_PROMPT
        )
    
    def get_tools(self) -> List:
        """Get inventory-specific tools.
        
        Returns:
            List of 2 inventory tools
        """
        return [
            query_inventory_levels,
            check_safety_stock_violations
        ]

"""Supplier specialist agent."""

from typing import List
from .base_agent import BaseAgent
from ..config.prompts import SUPPLIER_AGENT_PROMPT
from ..tools.supplier_tools import find_alternative_suppliers, get_supplier_lead_times


class SupplierAgent(BaseAgent):
    """Supplier specialist agent with isolated tool access."""
    
    def __init__(self):
        """Initialize supplier agent."""
        super().__init__(
            name="SupplierAgent",
            system_prompt=SUPPLIER_AGENT_PROMPT
        )
    
    def get_tools(self) -> List:
        """Get supplier-specific tools.
        
        Returns:
            List of 2 supplier tools
        """
        return [
            find_alternative_suppliers,
            get_supplier_lead_times
        ]

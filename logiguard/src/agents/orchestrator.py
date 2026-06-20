"""Orchestrator agent for query routing and coordination."""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from .inventory_agent import InventoryAgent
from .shipment_agent import ShipmentAgent
from .disruption_agent import DisruptionAgent
from .supplier_agent import SupplierAgent
from ..config.prompts import ORCHESTRATOR_PROMPT
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OrchestratorAgent(BaseAgent):
    """Orchestrator agent that routes queries to specialist agents."""
    
    def __init__(self):
        """Initialize orchestrator agent."""
        super().__init__(
            name="OrchestratorAgent",
            system_prompt=ORCHESTRATOR_PROMPT
        )
        
        # Initialize specialist agents
        self.inventory_agent = InventoryAgent()
        self.shipment_agent = ShipmentAgent()
        self.disruption_agent = DisruptionAgent()
        self.supplier_agent = SupplierAgent()
        
        logger.info("Orchestrator initialized with 4 specialist agents")
    
    def get_tools(self) -> List:
        """Orchestrator doesn't use tools directly.
        
        Returns:
            Empty list (orchestrator delegates to specialist agents)
        """
        return []
    
    def route_query(self, query: str) -> str:
        """Determine which specialist agent(s) should handle the query.
        
        Args:
            query: User query
        
        Returns:
            Agent type identifier
        """
        query_lower = query.lower()
        
        # Keyword-based routing
        if any(keyword in query_lower for keyword in ['inventory', 'stock', 'sku', 'safety stock', 'reorder']):
            return 'inventory'
        elif any(keyword in query_lower for keyword in ['shipment', 'delivery', 'eta', 'transit', 'carrier']):
            return 'shipment'
        elif any(keyword in query_lower for keyword in ['disruption', 'risk', 'incident', 'delay', 'port']):
            return 'disruption'
        elif any(keyword in query_lower for keyword in ['supplier', 'vendor', 'alternative', 'lead time']):
            return 'supplier'
        else:
            # Default to inventory for ambiguous queries
            return 'inventory'
    
    def execute(self, query: str) -> Dict[str, Any]:
        """Execute orchestrator with query routing.
        
        Args:
            query: User query
        
        Returns:
            Synthesized response from specialist agent(s)
        """
        try:
            logger.info(f"Orchestrator routing query: {query[:100]}...")
            
            # Route to appropriate specialist
            agent_type = self.route_query(query)
            logger.info(f"Routing to {agent_type} agent")
            
            # Execute specialist agent
            if agent_type == 'inventory':
                result = self.inventory_agent.execute(query)
            elif agent_type == 'shipment':
                result = self.shipment_agent.execute(query)
            elif agent_type == 'disruption':
                result = self.disruption_agent.execute(query)
            elif agent_type == 'supplier':
                result = self.supplier_agent.execute(query)
            else:
                result = {
                    'status': 'error',
                    'message': f"Unknown agent type: {agent_type}"
                }
            
            # Add orchestrator metadata
            result['orchestrator'] = {
                'routed_to': agent_type,
                'query': query
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Orchestrator execution failed: {str(e)}")
            return {
                'status': 'error',
                'agent': 'OrchestratorAgent',
                'error': str(e),
                'message': f"Orchestrator failed: {str(e)}"
            }
    
    def execute_multi_agent(self, query: str, agent_types: List[str]) -> Dict[str, Any]:
        """Execute multiple specialist agents for complex queries.
        
        Args:
            query: User query
            agent_types: List of agent types to execute
        
        Returns:
            Synthesized response from multiple agents
        """
        results = {}
        
        for agent_type in agent_types:
            if agent_type == 'inventory':
                results['inventory'] = self.inventory_agent.execute(query)
            elif agent_type == 'shipment':
                results['shipment'] = self.shipment_agent.execute(query)
            elif agent_type == 'disruption':
                results['disruption'] = self.disruption_agent.execute(query)
            elif agent_type == 'supplier':
                results['supplier'] = self.supplier_agent.execute(query)
        
        # Synthesize results
        return {
            'status': 'success',
            'agent': 'OrchestratorAgent',
            'multi_agent_results': results,
            'message': f"Executed {len(agent_types)} specialist agents"
        }

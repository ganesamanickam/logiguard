"""Base agent abstract class."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..config.settings import get_settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, system_prompt: str):
        """Initialize base agent.
        
        Args:
            name: Agent name
            system_prompt: System prompt for the agent
        """
        self.name = name
        self.system_prompt = system_prompt
        self.settings = get_settings()
        
        # Initialize LLM with temperature=0.0
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=self.settings.openai_temperature,
            api_key=self.settings.openai_api_key
        )
        
        logger.info(f"Initialized {name} (temperature={self.settings.openai_temperature})")
    
    @abstractmethod
    def get_tools(self) -> List:
        """Get list of tools available to this agent.
        
        Returns:
            List of tool functions
        """
        pass
    
    def create_agent_executor(self) -> AgentExecutor:
        """Create LangChain agent executor.
        
        Returns:
            Configured AgentExecutor
        """
        tools = self.get_tools()
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def execute(self, query: str) -> Dict[str, Any]:
        """Execute agent with query.
        
        Args:
            query: User query
        
        Returns:
            Agent response dictionary
        """
        try:
            logger.info(f"{self.name} executing query: {query[:100]}...")
            
            agent_executor = self.create_agent_executor()
            result = agent_executor.invoke({"input": query})
            
            return {
                'status': 'success',
                'agent': self.name,
                'output': result.get('output', ''),
                'intermediate_steps': result.get('intermediate_steps', [])
            }
        
        except Exception as e:
            logger.error(f"{self.name} execution failed: {str(e)}")
            return {
                'status': 'error',
                'agent': self.name,
                'error': str(e),
                'message': f"Agent execution failed: {str(e)}"
            }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}')"

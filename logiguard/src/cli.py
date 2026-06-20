"""Terminal interface for LogiGuard system."""

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import box
from .agents.orchestrator import OrchestratorAgent
from .agents.guardrail_agent import GuardrailAgent
from .utils.validators import sanitize_query
from .utils.logger import get_logger
from .utils.exceptions import DataValidationError

logger = get_logger(__name__)
console = Console()


class CLIInterface:
    """Interactive terminal interface for LogiGuard."""
    
    EXAMPLE_QUERIES = [
        "What is the current inventory level for SKU-00001 in Asia?",
        "Show me all shipments delayed by more than 5 days",
        "Are there any active disruptions in Europe?",
        "Find alternative suppliers for SKU-00050",
        "Check safety stock violations in North America",
        "What is the delivery window for SHIP-000100?"
    ]
    
    def __init__(self):
        """Initialize CLI interface."""
        self.orchestrator = OrchestratorAgent()
        self.guardrail = GuardrailAgent()
        self.running = False
        
        logger.info("CLI Interface initialized")
    
    def display_welcome(self):
        """Display welcome banner."""
        welcome_text = """
# LogiGuard Supply Chain Decision Support System

**AI-powered supply chain risk identification and decision support**

## Features
- 🔍 Real-time inventory analysis
- 📦 Shipment tracking and ETA calculation
- ⚠️  Disruption monitoring and risk assessment
- 🏭 Supplier evaluation and alternatives

## Safety Guarantees
- ✅ Temperature=0.0 (deterministic responses)
- ✅ PII masking enabled
- ✅ Read-only operations only
- ✅ Uncertainty enforcement for missing data
        """
        
        console.print(Panel(Markdown(welcome_text), border_style="blue", box=box.DOUBLE))
        
        # Display example queries
        table = Table(title="Example Queries", box=box.SIMPLE)
        table.add_column("Query", style="cyan")
        
        for query in self.EXAMPLE_QUERIES:
            table.add_row(query)
        
        console.print(table)
        console.print()
    
    def display_help(self):
        """Display help information."""
        help_text = """
## Available Commands

- `query <your question>` - Ask a supply chain question
- `status` - Show system status
- `logs` - View recent activity
- `help` - Show this help message
- `exit` or `quit` - Exit the application

## Query Examples

**Inventory Queries:**
- "What is the stock level for SKU-12345?"
- "Check safety stock violations in Asia"

**Shipment Queries:**
- "Get status of shipment SHIP-000001"
- "Calculate delivery window for SHIP-000050"

**Disruption Queries:**
- "Are there disruptions in Europe?"
- "Assess regional risk for North America"

**Supplier Queries:**
- "Find alternative suppliers for SKU-00100"
- "Get lead times for supplier SUP-0025"
        """
        
        console.print(Panel(Markdown(help_text), title="Help", border_style="green"))
    
    def display_status(self):
        """Display system status."""
        status_table = Table(title="System Status", box=box.ROUNDED)
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        
        status_table.add_row("Orchestrator Agent", "✓ Active")
        status_table.add_row("Inventory Agent", "✓ Active")
        status_table.add_row("Shipment Agent", "✓ Active")
        status_table.add_row("Disruption Agent", "✓ Active")
        status_table.add_row("Supplier Agent", "✓ Active")
        status_table.add_row("Guardrail Agent", "✓ Active")
        status_table.add_row("PII Masking", "✓ Enabled")
        status_table.add_row("Read-Only Enforcement", "✓ Enabled")
        status_table.add_row("Uncertainty Validation", "✓ Enabled")
        
        console.print(status_table)
    
    def handle_query(self, query: str) -> None:
        """Handle user query.
        
        Args:
            query: User query string
        """
        try:
            # Sanitize query
            query = sanitize_query(query)
            
            # Display processing message
            with console.status("[bold blue]Processing query...", spinner="dots"):
                # Execute orchestrator
                result = self.orchestrator.execute(query)
                
                # Validate with guardrail
                is_valid, error, validated_output = self.guardrail.validate(
                    result,
                    context={'query': query}
                )
            
            # Display result
            if result.get('status') == 'success':
                output_text = result.get('output', 'No output generated')
                
                # Apply final sanitization
                sanitized = self.guardrail.sanitize_output(output_text)
                
                console.print(Panel(
                    sanitized,
                    title=f"Response from {result.get('orchestrator', {}).get('routed_to', 'Agent')} Agent",
                    border_style="green",
                    box=box.ROUNDED
                ))
                
                # Show metadata if available
                if result.get('orchestrator'):
                    console.print(f"[dim]Routed to: {result['orchestrator']['routed_to']} agent[/dim]")
            else:
                error_msg = result.get('error', result.get('message', 'Unknown error'))
                console.print(Panel(
                    f"[red]Error:[/red] {error_msg}",
                    title="Error",
                    border_style="red"
                ))
        
        except DataValidationError as e:
            console.print(f"[red]Validation Error:[/red] {str(e)}")
        except Exception as e:
            logger.error(f"Query handling error: {str(e)}")
            console.print(f"[red]Error:[/red] {str(e)}")
    
    def run(self):
        """Run the interactive CLI."""
        self.running = True
        self.display_welcome()
        
        console.print("[bold green]LogiGuard is ready![/bold green]")
        console.print("Type 'help' for commands or enter your query.\n")
        
        while self.running:
            try:
                # Get user input
                user_input = console.input("[bold cyan]LogiGuard>[/bold cyan] ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                command = user_input.lower()
                
                if command in ['exit', 'quit']:
                    console.print("[yellow]Goodbye![/yellow]")
                    self.running = False
                    break
                
                elif command == 'help':
                    self.display_help()
                
                elif command == 'status':
                    self.display_status()
                
                elif command == 'logs':
                    console.print("[yellow]Log viewing not yet implemented. Check logs/ directory.[/yellow]")
                
                else:
                    # Treat as query
                    self.handle_query(user_input)
                
                console.print()  # Add spacing
            
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit.[/yellow]")
            except EOFError:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                logger.error(f"CLI error: {str(e)}")
                console.print(f"[red]Error:[/red] {str(e)}")


def main():
    """Main entry point for CLI."""
    cli = CLIInterface()
    cli.run()


if __name__ == "__main__":
    main()

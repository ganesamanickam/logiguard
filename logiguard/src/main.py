"""Main application entry point."""

import sys
import io
from pathlib import Path
from .cli import CLIInterface
from .data.generator import DataGenerator
from .config.settings import get_settings
from .utils.logger import get_logger
from .utils.exceptions import ConfigurationError

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logger = get_logger(__name__)


def initialize_system() -> bool:
    """Initialize LogiGuard system.
    
    Returns:
        True if initialization successful
    """
    try:
        logger.info("Initializing LogiGuard system...")
        
        # Load and validate settings
        settings = get_settings()
        logger.info(f"Settings loaded (model={settings.openai_model}, temp={settings.openai_temperature})")
        
        # Check if data files exist
        data_dir = Path(settings.data_dir)
        required_files = ['inventory.csv', 'shipments.csv', 'disruptions.csv', 'suppliers.csv']
        
        missing_files = []
        for filename in required_files:
            if not (data_dir / filename).exists():
                missing_files.append(filename)
        
        # Generate data if missing
        if missing_files:
            logger.warning(f"Missing data files: {missing_files}")
            print(f"\n⚠️  Missing data files: {', '.join(missing_files)}")
            print("Generating data files...")
            
            generator = DataGenerator(data_dir=settings.data_dir)
            generator.generate_all()
            
            print("✓ Data files generated successfully\n")
        
        logger.info("System initialization complete")
        return True
    
    except ConfigurationError as e:
        logger.error(f"Configuration error: {str(e)}")
        print(f"\n❌ Configuration Error: {str(e)}")
        print("\nPlease ensure:")
        print("1. .env file exists (copy from .env.example)")
        print("2. OPENAI_API_KEY is set in .env")
        print("3. OPENAI_TEMPERATURE is set to 0.0")
        return False
    
    except Exception as e:
        logger.error(f"Initialization error: {str(e)}")
        print(f"\n❌ Initialization Error: {str(e)}")
        return False


def run_application():
    """Run the LogiGuard application."""
    try:
        # Initialize system
        if not initialize_system():
            sys.exit(1)
        
        # Start CLI
        cli = CLIInterface()
        cli.run()
    
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"\n❌ Application Error: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   LogiGuard Supply Chain Decision Support System          ║
║   Version 1.0.0                                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    run_application()


if __name__ == "__main__":
    main()

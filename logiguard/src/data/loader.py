"""Data loading utilities with validation."""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from ..utils.exceptions import DataLoadError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataLoader:
    """Load and validate CSV datasets."""
    
    def __init__(self, data_dir: str = "./data"):
        """Initialize data loader.
        
        Args:
            data_dir: Directory containing CSV files
        """
        self.data_dir = Path(data_dir)
        self._cache: Dict[str, pd.DataFrame] = {}
    
    def load_inventory(self, use_cache: bool = True) -> pd.DataFrame:
        """Load inventory.csv.
        
        Args:
            use_cache: Use cached data if available
        
        Returns:
            DataFrame with inventory data
        
        Raises:
            DataLoadError: If file cannot be loaded
        """
        return self._load_csv('inventory.csv', use_cache)
    
    def load_shipments(self, use_cache: bool = True) -> pd.DataFrame:
        """Load shipments.csv.
        
        Args:
            use_cache: Use cached data if available
        
        Returns:
            DataFrame with shipment data
        
        Raises:
            DataLoadError: If file cannot be loaded
        """
        return self._load_csv('shipments.csv', use_cache)
    
    def load_disruptions(self, use_cache: bool = True) -> pd.DataFrame:
        """Load disruptions.csv.
        
        Args:
            use_cache: Use cached data if available
        
        Returns:
            DataFrame with disruption data
        
        Raises:
            DataLoadError: If file cannot be loaded
        """
        return self._load_csv('disruptions.csv', use_cache)
    
    def load_suppliers(self, use_cache: bool = True) -> pd.DataFrame:
        """Load suppliers.csv.
        
        Args:
            use_cache: Use cached data if available
        
        Returns:
            DataFrame with supplier data
        
        Raises:
            DataLoadError: If file cannot be loaded
        """
        return self._load_csv('suppliers.csv', use_cache)
    
    def _load_csv(self, filename: str, use_cache: bool = True) -> pd.DataFrame:
        """Load CSV file with caching and validation.
        
        Args:
            filename: Name of CSV file
            use_cache: Use cached data if available
        
        Returns:
            DataFrame with data
        
        Raises:
            DataLoadError: If file cannot be loaded
        """
        # Check cache
        if use_cache and filename in self._cache:
            logger.debug(f"Using cached data for {filename}")
            return self._cache[filename].copy()
        
        filepath = self.data_dir / filename
        
        # Check if file exists
        if not filepath.exists():
            raise DataLoadError(
                f"Data file not found: {filepath}. "
                f"Run 'python -m src.data.generator' to generate data."
            )
        
        try:
            # Load CSV
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {filename}: {len(df)} records")
            
            # Validate not empty
            if df.empty:
                raise DataLoadError(f"Data file is empty: {filename}")
            
            # Cache the data
            self._cache[filename] = df.copy()
            
            return df
        
        except pd.errors.EmptyDataError:
            raise DataLoadError(f"Data file is empty: {filename}")
        except pd.errors.ParserError as e:
            raise DataLoadError(f"Failed to parse {filename}: {str(e)}")
        except Exception as e:
            raise DataLoadError(f"Failed to load {filename}: {str(e)}")
    
    def clear_cache(self):
        """Clear cached data."""
        self._cache.clear()
        logger.debug("Data cache cleared")
    
    def validate_relational_integrity(self) -> Dict[str, Any]:
        """Validate relational integrity across datasets.
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Validating relational integrity...")
        
        results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        try:
            inventory = self.load_inventory()
            shipments = self.load_shipments()
            suppliers = self.load_suppliers()
            
            # Check SKU references
            inventory_skus = set(inventory['SKU'].unique())
            shipment_skus = set(shipments['SKU'].unique())
            
            # SKUs in shipments not in inventory (warning)
            missing_skus = shipment_skus - inventory_skus
            if missing_skus:
                results['warnings'].append(
                    f"Found {len(missing_skus)} SKUs in shipments not in inventory"
                )
            
            # Check region consistency
            inventory_regions = set(inventory['Region'].unique())
            shipment_regions = set(shipments['Region'].unique())
            supplier_regions = set(suppliers['Region'].unique())
            
            all_regions = inventory_regions | shipment_regions | supplier_regions
            logger.info(f"Found {len(all_regions)} unique regions across datasets")
            
            logger.info("Relational integrity validation complete")
            
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Validation failed: {str(e)}")
        
        return results

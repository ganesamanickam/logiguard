"""Supplier evaluation tools."""

from typing import Optional, Dict, Any, List
from langchain.tools import tool
import pandas as pd
from ..data.loader import DataLoader
from ..utils.validators import validate_sku, validate_region
from ..utils.logger import get_logger

logger = get_logger(__name__)


@tool
def find_alternative_suppliers(sku: str, exclude_region: Optional[str] = None) -> Dict[str, Any]:
    """Find alternative suppliers for a SKU.
    
    Args:
        sku: Product SKU identifier (e.g., 'SKU-00001')
        exclude_region: Optional region to exclude from results (e.g., 'Asia')
    
    Returns:
        Dictionary with list of alternative suppliers, lead times, and reliability scores
    """
    try:
        # Validate inputs
        sku = validate_sku(sku)
        if exclude_region:
            exclude_region = validate_region(exclude_region)
        
        logger.info(f"Finding alternative suppliers for SKU={sku}, exclude_region={exclude_region}")
        
        # Load supplier data
        loader = DataLoader()
        df = loader.load_suppliers()
        
        # Find suppliers that supply this SKU
        # SKUs_Supplied is comma-separated list
        suppliers = df[df['SKUs_Supplied'].str.contains(sku, na=False, regex=False)]
        
        # Exclude region if specified
        if exclude_region:
            suppliers = suppliers[suppliers['Region'] != exclude_region]
        
        # Check if no alternatives found (edge case)
        if suppliers.empty:
            return {
                'status': 'no_alternatives',
                'sku': sku,
                'exclude_region': exclude_region,
                'alternatives': [],
                'total_alternatives': 0,
                'message': f"No alternative suppliers found for {sku}" + 
                          (f" outside {exclude_region}" if exclude_region else "") +
                          ". ESCALATION REQUIRED: Contact procurement team for emergency sourcing."
            }
        
        # Sort by reliability score (highest first)
        suppliers = suppliers.sort_values('Reliability_Score', ascending=False)
        
        # Format alternatives
        alternatives = []
        for _, row in suppliers.iterrows():
            alternatives.append({
                'supplier_id': row['Supplier_ID'],
                'supplier_name': row['Supplier_Name'],
                'region': row['Region'],
                'avg_lead_time_days': int(row['Avg_Lead_Time_Days']),
                'reliability_score': float(row['Reliability_Score']),
                'backup_region': row['Backup_Region'] if pd.notna(row['Backup_Region']) else None
            })
        
        # Calculate regional distribution
        region_counts = suppliers['Region'].value_counts().to_dict()
        
        return {
            'status': 'success',
            'sku': sku,
            'exclude_region': exclude_region,
            'alternatives': alternatives,
            'total_alternatives': len(alternatives),
            'regional_distribution': region_counts,
            'best_option': alternatives[0] if alternatives else None,
            'message': f"Found {len(alternatives)} alternative suppliers for {sku}"
        }
    
    except Exception as e:
        logger.error(f"Error finding alternative suppliers: {str(e)}")
        return {
            'status': 'error',
            'message': f"Failed to find alternative suppliers: {str(e)}",
            'sku': sku
        }


@tool
def get_supplier_lead_times(supplier_id: str) -> Dict[str, Any]:
    """Get supplier lead time and reliability information.
    
    Args:
        supplier_id: Supplier ID (e.g., 'SUP-0001')
    
    Returns:
        Dictionary with average lead time, reliability score, and region
    """
    try:
        # Validate input (basic validation)
        if not supplier_id or not isinstance(supplier_id, str):
            return {
                'status': 'error',
                'message': 'Supplier ID must be a non-empty string'
            }
        
        supplier_id = supplier_id.upper()
        
        logger.info(f"Getting lead times for supplier={supplier_id}")
        
        # Load supplier data
        loader = DataLoader()
        df = loader.load_suppliers()
        
        # Find supplier
        result = df[df['Supplier_ID'] == supplier_id]
        
        # Check if supplier found
        if result.empty:
            # Edge case: missing supplier - return warning with partial data
            return {
                'status': 'not_found',
                'supplier_id': supplier_id,
                'message': f"Supplier {supplier_id} not found in database. " +
                          "WARNING: Unable to provide lead time information. " +
                          "Consider using find_alternative_suppliers tool.",
                'avg_lead_time_days': None,
                'reliability_score': None,
                'region': None
            }
        
        record = result.iloc[0]
        
        # Parse SKUs supplied
        skus_supplied = [sku.strip() for sku in record['SKUs_Supplied'].split(',')]
        
        # Determine reliability category
        reliability = float(record['Reliability_Score'])
        if reliability >= 95:
            reliability_category = 'EXCELLENT'
        elif reliability >= 85:
            reliability_category = 'GOOD'
        elif reliability >= 75:
            reliability_category = 'FAIR'
        else:
            reliability_category = 'POOR'
        
        return {
            'status': 'success',
            'supplier_id': record['Supplier_ID'],
            'supplier_name': record['Supplier_Name'],
            'region': record['Region'],
            'avg_lead_time_days': int(record['Avg_Lead_Time_Days']),
            'reliability_score': reliability,
            'reliability_category': reliability_category,
            'skus_supplied': skus_supplied,
            'total_skus': len(skus_supplied),
            'backup_region': record['Backup_Region'] if pd.notna(record['Backup_Region']) else None,
            'message': f"Supplier {record['Supplier_Name']}: {int(record['Avg_Lead_Time_Days'])} days lead time, {reliability}% reliability ({reliability_category})"
        }
    
    except Exception as e:
        logger.error(f"Error getting supplier lead times: {str(e)}")
        return {
            'status': 'error',
            'message': f"Failed to get supplier lead times: {str(e)}",
            'supplier_id': supplier_id
        }

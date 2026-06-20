"""Inventory analysis tools."""

from typing import Optional, Dict, Any, List
from langchain.tools import tool
import pandas as pd
from ..data.loader import DataLoader
from ..utils.validators import validate_sku, validate_region
from ..utils.logger import get_logger

logger = get_logger(__name__)


@tool
def query_inventory_levels(sku: str, region: Optional[str] = None) -> Dict[str, Any]:
    """Query current inventory levels for a SKU.
    
    Args:
        sku: Product SKU identifier (e.g., 'SKU-00001')
        region: Optional region filter (e.g., 'Asia', 'Europe')
    
    Returns:
        Dictionary with inventory data including current stock, safety stock, and status
    """
    try:
        # Validate inputs
        sku = validate_sku(sku)
        if region:
            region = validate_region(region)
        
        logger.info(f"Querying inventory for SKU={sku}, Region={region}")
        
        # Load inventory data
        loader = DataLoader()
        df = loader.load_inventory()
        
        # Filter by SKU
        result = df[df['SKU'] == sku]
        
        # Filter by region if provided
        if region:
            result = result[result['Region'] == region]
        
        # Check if SKU found
        if result.empty:
            return {
                'status': 'not_found',
                'message': f"SKU {sku} not found" + (f" in region {region}" if region else ""),
                'sku': sku,
                'region': region
            }
        
        # Get first matching record
        record = result.iloc[0]
        
        # Determine status
        current_stock = int(record['Current_Stock'])
        safety_stock = int(record['Safety_Stock'])
        
        if current_stock == 0:
            status = 'OUT_OF_STOCK'
        elif current_stock < safety_stock:
            status = 'CRITICAL'
        elif current_stock < safety_stock * 1.5:
            status = 'WARNING'
        else:
            status = 'OK'
        
        return {
            'status': 'success',
            'sku': sku,
            'product_name': record['Product_Name'],
            'category': record['Category'],
            'current_stock': current_stock,
            'safety_stock': safety_stock,
            'reorder_point': int(record['Reorder_Point']),
            'region': record['Region'],
            'stock_status': status,
            'last_updated': record['Last_Updated'],
            'message': f"Current stock: {current_stock} units (Safety stock: {safety_stock})"
        }
    
    except Exception as e:
        logger.error(f"Error querying inventory: {str(e)}")
        return {
            'status': 'error',
            'message': f"Failed to query inventory: {str(e)}",
            'sku': sku
        }


@tool
def check_safety_stock_violations(region: Optional[str] = None) -> Dict[str, Any]:
    """Check for SKUs below safety stock threshold.
    
    Args:
        region: Optional region filter (e.g., 'Asia', 'Europe')
    
    Returns:
        Dictionary with list of violations and severity levels
    """
    try:
        # Validate region
        if region:
            region = validate_region(region)
        
        logger.info(f"Checking safety stock violations for Region={region}")
        
        # Load inventory data
        loader = DataLoader()
        df = loader.load_inventory()
        
        # Filter by region if provided
        if region:
            df = df[df['Region'] == region]
        
        # Find violations (current stock < safety stock)
        violations = df[df['Current_Stock'] < df['Safety_Stock']].copy()
        
        # Check if no violations
        if violations.empty:
            return {
                'status': 'OK',
                'violations': [],
                'total_violations': 0,
                'region': region,
                'message': 'No safety stock violations found' + (f' in {region}' if region else '')
            }
        
        # Calculate severity
        violations['shortage_pct'] = (
            (violations['Safety_Stock'] - violations['Current_Stock']) / 
            violations['Safety_Stock'] * 100
        ).round(1)
        
        violations['severity'] = violations['shortage_pct'].apply(
            lambda x: 'CRITICAL' if x >= 50 else 'HIGH' if x >= 25 else 'MEDIUM'
        )
        
        # Sort by severity
        violations = violations.sort_values('shortage_pct', ascending=False)
        
        # Format results
        violation_list = []
        for _, row in violations.iterrows():
            violation_list.append({
                'sku': row['SKU'],
                'product_name': row['Product_Name'],
                'category': row['Category'],
                'current_stock': int(row['Current_Stock']),
                'safety_stock': int(row['Safety_Stock']),
                'shortage_pct': float(row['shortage_pct']),
                'severity': row['severity'],
                'region': row['Region']
            })
        
        return {
            'status': 'VIOLATIONS_FOUND',
            'violations': violation_list,
            'total_violations': len(violation_list),
            'region': region,
            'critical_count': len([v for v in violation_list if v['severity'] == 'CRITICAL']),
            'high_count': len([v for v in violation_list if v['severity'] == 'HIGH']),
            'message': f"Found {len(violation_list)} safety stock violations" + (f' in {region}' if region else '')
        }
    
    except Exception as e:
        logger.error(f"Error checking safety stock violations: {str(e)}")
        return {
            'status': 'error',
            'message': f"Failed to check violations: {str(e)}",
            'violations': []
        }

"""Disruption monitoring tools."""

from typing import Dict, Any, List
from langchain.tools import tool
import pandas as pd
from datetime import datetime, timedelta
from ..data.loader import DataLoader
from ..utils.validators import validate_region
from ..utils.logger import get_logger

logger = get_logger(__name__)


@tool
def check_active_disruptions(region: str) -> Dict[str, Any]:
    """Check for active disruptions in a region.
    
    Args:
        region: Region identifier (e.g., 'Asia', 'Europe', 'North America')
    
    Returns:
        Dictionary with list of active disruptions and severity levels (1-5)
    """
    try:
        # Validate input
        region = validate_region(region)
        
        logger.info(f"Checking active disruptions for region={region}")
        
        # Load disruption data
        loader = DataLoader()
        df = loader.load_disruptions()
        
        # Filter by region
        result = df[df['Region'] == region]
        
        if result.empty:
            return {
                'status': 'OK',
                'region': region,
                'active_disruptions': [],
                'total_disruptions': 0,
                'message': f"No disruptions found in {region}"
            }
        
        # Filter for active disruptions (recent start dates)
        today = datetime.now()
        result['Start_Date_dt'] = pd.to_datetime(result['Start_Date'])
        
        # Consider disruptions from last 30 days as potentially active
        active = result[result['Start_Date_dt'] >= (today - timedelta(days=30))]
        
        if active.empty:
            return {
                'status': 'OK',
                'region': region,
                'active_disruptions': [],
                'total_disruptions': 0,
                'message': f"No active disruptions in {region}"
            }
        
        # Sort by severity (highest first)
        active = active.sort_values('Severity', ascending=False)
        
        # Format disruptions
        disruptions = []
        for _, row in active.iterrows():
            disruptions.append({
                'disruption_id': row['Disruption_ID'],
                'type': row['Type'],
                'severity': int(row['Severity']),
                'start_date': row['Start_Date'],
                'expected_resolution': row['Expected_Resolution'] if pd.notna(row['Expected_Resolution']) else 'UNCERTAIN',
                'affected_ports': row['Affected_Ports'],
                'description': row['Description']
            })
        
        # Calculate risk level
        max_severity = active['Severity'].max()
        if max_severity >= 4:
            risk_level = 'HIGH'
        elif max_severity >= 3:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'status': 'DISRUPTIONS_FOUND',
            'region': region,
            'active_disruptions': disruptions,
            'total_disruptions': len(disruptions),
            'max_severity': int(max_severity),
            'risk_level': risk_level,
            'message': f"Found {len(disruptions)} active disruptions in {region} (Max severity: {int(max_severity)})"
        }
    
    except Exception as e:
        logger.error(f"Error checking disruptions: {str(e)}")
        return {
            'status': 'error',
            'message': f"Failed to check disruptions: {str(e)}",
            'region': region
        }


@tool
def assess_regional_risk(region: str) -> Dict[str, Any]:
    """Assess overall risk level for a region.
    
    Args:
        region: Region identifier (e.g., 'Asia', 'Europe', 'North America')
    
    Returns:
        Dictionary with risk level, active disruptions, and affected shipments
    """
    try:
        # Validate input
        region = validate_region(region)
        
        logger.info(f"Assessing regional risk for {region}")
        
        # Load data
        loader = DataLoader()
        disruptions_df = loader.load_disruptions()
        shipments_df = loader.load_shipments()
        inventory_df = loader.load_inventory()
        
        # Get active disruptions
        today = datetime.now()
        disruptions_df['Start_Date_dt'] = pd.to_datetime(disruptions_df['Start_Date'])
        active_disruptions = disruptions_df[
            (disruptions_df['Region'] == region) &
            (disruptions_df['Start_Date_dt'] >= (today - timedelta(days=30)))
        ]
        
        # Get affected shipments
        affected_shipments = shipments_df[
            (shipments_df['Region'] == region) &
            (shipments_df['Status'].isin(['Delayed', 'Customs Hold']))
        ]
        
        # Get inventory status
        inventory_region = inventory_df[inventory_df['Region'] == region]
        low_stock_items = inventory_region[
            inventory_region['Current_Stock'] < inventory_region['Safety_Stock']
        ]
        
        # Calculate risk factors
        disruption_risk = 0
        if len(active_disruptions) > 0:
            max_severity = active_disruptions['Severity'].max()
            disruption_risk = max_severity * 20  # 0-100 scale
        
        shipment_risk = min(len(affected_shipments) * 5, 100)  # Cap at 100
        inventory_risk = min(len(low_stock_items) * 10, 100)  # Cap at 100
        
        # Overall risk (weighted average)
        overall_risk = (
            disruption_risk * 0.5 +
            shipment_risk * 0.3 +
            inventory_risk * 0.2
        )
        
        # Determine risk level
        if overall_risk >= 70:
            risk_level = 'HIGH'
        elif overall_risk >= 40:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # Handle conflicting data (edge case)
        if len(low_stock_items) == 0 and len(active_disruptions) > 0:
            if active_disruptions['Severity'].max() >= 4:
                risk_level = 'MEDIUM'  # Future risk despite current stock
        
        return {
            'status': 'success',
            'region': region,
            'risk_level': risk_level,
            'overall_risk_score': round(overall_risk, 1),
            'active_disruptions': len(active_disruptions),
            'affected_shipments': len(affected_shipments),
            'low_stock_items': len(low_stock_items),
            'risk_factors': {
                'disruption_risk': round(disruption_risk, 1),
                'shipment_risk': round(shipment_risk, 1),
                'inventory_risk': round(inventory_risk, 1)
            },
            'message': f"Regional risk for {region}: {risk_level} (Score: {round(overall_risk, 1)}/100)"
        }
    
    except Exception as e:
        logger.error(f"Error assessing regional risk: {str(e)}")
        return {
            'status': 'error',
            'message': f"Failed to assess regional risk: {str(e)}",
            'region': region
        }

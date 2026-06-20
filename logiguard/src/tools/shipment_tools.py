"""Shipment tracking tools."""

from typing import Optional, Dict, Any
from langchain.tools import tool
import pandas as pd
from datetime import datetime, timedelta
from ..data.loader import DataLoader
from ..utils.validators import validate_shipment_id, validate_region
from ..utils.logger import get_logger

logger = get_logger(__name__)


@tool
def get_shipment_status(shipment_id: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
    """Get shipment status and ETA information.
    
    Args:
        shipment_id: Optional shipment ID (e.g., 'SHIP-000001')
        region: Optional region filter (e.g., 'Asia', 'Europe')
    
    Returns:
        Dictionary with shipment status, origin, destination, ETA, and delay information
    """
    try:
        # Validate inputs
        if shipment_id:
            shipment_id = validate_shipment_id(shipment_id)
        if region:
            region = validate_region(region)
        
        if not shipment_id and not region:
            return {
                'status': 'error',
                'message': 'Either shipment_id or region must be provided'
            }
        
        logger.info(f"Getting shipment status for ID={shipment_id}, Region={region}")
        
        # Load shipment data
        loader = DataLoader()
        df = loader.load_shipments()
        
        # Filter by shipment ID or region
        if shipment_id:
            result = df[df['Shipment_ID'] == shipment_id]
        else:
            result = df[df['Region'] == region]
        
        # Check if found
        if result.empty:
            return {
                'status': 'not_found',
                'message': f"No shipments found for " + (f"ID {shipment_id}" if shipment_id else f"region {region}"),
                'shipment_id': shipment_id,
                'region': region
            }
        
        # If single shipment requested
        if shipment_id:
            record = result.iloc[0]
            
            # Handle NULL adjusted delivery (edge case)
            adjusted_delivery = record['Adjusted_Delivery']
            has_null_eta = pd.isna(adjusted_delivery)
            
            # Calculate delay
            if not has_null_eta:
                expected = pd.to_datetime(record['Expected_Delivery'])
                adjusted = pd.to_datetime(adjusted_delivery)
                delay_days = (adjusted - expected).days
            else:
                delay_days = None
            
            return {
                'status': 'success',
                'shipment_id': record['Shipment_ID'],
                'sku': record['SKU'],
                'quantity': int(record['Quantity']),
                'origin_port': record['Origin_Port'],
                'destination_port': record['Destination_Port'],
                'ship_date': record['Ship_Date'],
                'expected_delivery': record['Expected_Delivery'],
                'adjusted_delivery': 'UNCERTAIN' if has_null_eta else adjusted_delivery,
                'eta_confidence': 'LOW' if has_null_eta else 'HIGH',
                'shipment_status': record['Status'],
                'carrier': record['Carrier'],
                'region': record['Region'],
                'delay_days': delay_days,
                'has_null_data': has_null_eta,
                'message': 'Delivery date is uncertain due to ongoing disruptions' if has_null_eta else f"Shipment {record['Status']}"
            }
        
        # Multiple shipments (region query)
        else:
            shipments = []
            for _, row in result.iterrows():
                has_null_eta = pd.isna(row['Adjusted_Delivery'])
                shipments.append({
                    'shipment_id': row['Shipment_ID'],
                    'sku': row['SKU'],
                    'status': row['Status'],
                    'destination_port': row['Destination_Port'],
                    'expected_delivery': row['Expected_Delivery'],
                    'adjusted_delivery': 'UNCERTAIN' if has_null_eta else row['Adjusted_Delivery'],
                    'has_uncertainty': has_null_eta
                })
            
            return {
                'status': 'success',
                'region': region,
                'total_shipments': len(shipments),
                'shipments': shipments[:10],  # Limit to 10 for readability
                'message': f"Found {len(shipments)} shipments in {region}"
            }
    
    except Exception as e:
        logger.error(f"Error getting shipment status: {str(e)}")
        return {
            'status': 'error',
            'message': f"Failed to get shipment status: {str(e)}"
        }


@tool
def calculate_delivery_windows(shipment_id: str) -> Dict[str, Any]:
    """Calculate delivery time windows with confidence ranges.
    
    Args:
        shipment_id: Shipment ID (e.g., 'SHIP-000001')
    
    Returns:
        Dictionary with estimated arrival range, min/max days, and confidence level
    """
    try:
        # Validate input
        shipment_id = validate_shipment_id(shipment_id)
        
        logger.info(f"Calculating delivery window for {shipment_id}")
        
        # Load shipment data
        loader = DataLoader()
        shipments_df = loader.load_shipments()
        disruptions_df = loader.load_disruptions()
        
        # Find shipment
        result = shipments_df[shipments_df['Shipment_ID'] == shipment_id]
        
        if result.empty:
            return {
                'status': 'not_found',
                'message': f"Shipment {shipment_id} not found",
                'shipment_id': shipment_id
            }
        
        record = result.iloc[0]
        
        # Check for active disruptions in destination region
        active_disruptions = disruptions_df[
            (disruptions_df['Region'] == record['Region']) &
            (disruptions_df['Severity'] >= 3)
        ]
        
        has_disruptions = len(active_disruptions) > 0
        
        # Calculate base delivery window
        ship_date = pd.to_datetime(record['Ship_Date'])
        expected_delivery = pd.to_datetime(record['Expected_Delivery'])
        base_days = (expected_delivery - ship_date).days
        
        # Adjust for disruptions
        if has_disruptions:
            max_severity = active_disruptions['Severity'].max()
            disruption_buffer = max_severity * 2  # 2 days per severity level
            min_days = base_days
            max_days = base_days + disruption_buffer
            confidence = 'LOW' if max_severity >= 4 else 'MEDIUM'
        else:
            min_days = base_days - 2
            max_days = base_days + 2
            confidence = 'HIGH'
        
        # Handle NULL adjusted delivery
        has_null_eta = pd.isna(record['Adjusted_Delivery'])
        
        return {
            'status': 'success',
            'shipment_id': shipment_id,
            'estimated_arrival': f"RANGE: {min_days}-{max_days} days from ship date",
            'min_days': min_days,
            'max_days': max_days,
            'confidence': confidence,
            'ship_date': record['Ship_Date'],
            'expected_delivery': record['Expected_Delivery'],
            'has_active_disruptions': has_disruptions,
            'disruption_count': len(active_disruptions),
            'has_null_data': has_null_eta,
            'message': f"Delivery window: {min_days}-{max_days} days (Confidence: {confidence})"
        }
    
    except Exception as e:
        logger.error(f"Error calculating delivery window: {str(e)}")
        return {
            'status': 'error',
            'message': f"Failed to calculate delivery window: {str(e)}"
        }

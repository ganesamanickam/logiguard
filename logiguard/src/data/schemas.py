"""Data schemas and validation models."""

from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, validator


class InventoryRecord(BaseModel):
    """Inventory data schema."""
    
    SKU: str = Field(..., description="Product SKU identifier")
    Product_Name: str = Field(..., description="Product name")
    Category: str = Field(..., description="Product category")
    Current_Stock: int = Field(..., ge=0, description="Current stock level")
    Safety_Stock: int = Field(..., ge=0, description="Safety stock threshold")
    Reorder_Point: int = Field(..., ge=0, description="Reorder point")
    Unit_Cost: float = Field(..., gt=0, description="Unit cost")
    Region: str = Field(..., description="Geographic region")
    Last_Updated: str = Field(..., description="Last update timestamp")
    
    @validator('SKU', 'Product_Name', 'Category', 'Region')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True


class ShipmentRecord(BaseModel):
    """Shipment data schema."""
    
    Shipment_ID: str = Field(..., description="Shipment identifier")
    SKU: str = Field(..., description="Product SKU")
    Quantity: int = Field(..., gt=0, description="Shipment quantity")
    Origin_Port: str = Field(..., description="Origin port")
    Destination_Port: str = Field(..., description="Destination port")
    Ship_Date: str = Field(..., description="Ship date")
    Expected_Delivery: str = Field(..., description="Expected delivery date")
    Adjusted_Delivery: Optional[str] = Field(None, description="Adjusted delivery date (may be NULL)")
    Status: str = Field(..., description="Shipment status")
    Carrier: str = Field(..., description="Carrier name")
    Region: str = Field(..., description="Destination region")
    
    @validator('Shipment_ID', 'SKU', 'Origin_Port', 'Destination_Port', 'Status', 'Carrier', 'Region')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True


class DisruptionRecord(BaseModel):
    """Disruption data schema."""
    
    Disruption_ID: str = Field(..., description="Disruption identifier")
    Region: str = Field(..., description="Affected region")
    Type: str = Field(..., description="Disruption type")
    Severity: int = Field(..., ge=1, le=5, description="Severity level (1-5)")
    Start_Date: str = Field(..., description="Start date")
    Expected_Resolution: Optional[str] = Field(None, description="Expected resolution date")
    Affected_Ports: str = Field(..., description="Affected ports (comma-separated)")
    Description: str = Field(..., description="Disruption description")
    
    @validator('Disruption_ID', 'Region', 'Type', 'Affected_Ports', 'Description')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True


class SupplierRecord(BaseModel):
    """Supplier data schema."""
    
    Supplier_ID: str = Field(..., description="Supplier identifier")
    Supplier_Name: str = Field(..., description="Supplier name")
    Region: str = Field(..., description="Supplier region")
    SKUs_Supplied: str = Field(..., description="SKUs supplied (comma-separated)")
    Avg_Lead_Time_Days: int = Field(..., ge=0, description="Average lead time in days")
    Reliability_Score: float = Field(..., ge=0, le=100, description="Reliability score (0-100)")
    Contact_Email: str = Field(..., description="Contact email")
    Backup_Region: Optional[str] = Field(None, description="Backup region")
    
    @validator('Supplier_ID', 'Supplier_Name', 'Region', 'SKUs_Supplied', 'Contact_Email')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True

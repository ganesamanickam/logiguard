"""CSV data generation for LogiGuard system."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import random


class DataGenerator:
    """Generate realistic supply chain CSV datasets."""
    
    # Standard regions for consistency
    REGIONS = ["North America", "Europe", "Asia", "South America", "Africa"]
    
    # Standard categories
    CATEGORIES = ["Electronics", "Apparel", "Food", "Automotive", "Pharmaceuticals"]
    
    # Ports by region
    PORTS = {
        "North America": ["Los Angeles", "New York", "Houston", "Vancouver"],
        "Europe": ["Rotterdam", "Hamburg", "Antwerp", "Southampton"],
        "Asia": ["Shanghai", "Singapore", "Hong Kong", "Tokyo"],
        "South America": ["Santos", "Buenos Aires", "Valparaiso", "Cartagena"],
        "Africa": ["Durban", "Lagos", "Mombasa", "Alexandria"]
    }
    
    # Disruption types
    DISRUPTION_TYPES = [
        "Port Strike",
        "Weather Event",
        "Customs Delay",
        "Equipment Shortage",
        "Labor Shortage",
        "Geopolitical Event"
    ]
    
    # Shipment statuses
    SHIPMENT_STATUSES = ["In Transit", "Delayed", "At Port", "Delivered", "Customs Hold"]
    
    # Carriers
    CARRIERS = ["Maersk", "MSC", "CMA CGM", "COSCO", "Hapag-Lloyd", "ONE", "Evergreen"]
    
    def __init__(self, data_dir: str = "./data"):
        """Initialize data generator.
        
        Args:
            data_dir: Directory to save generated CSV files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Set random seed for reproducibility
        random.seed(42)
        np.random.seed(42)
    
    def generate_all(self) -> Dict[str, Path]:
        """Generate all CSV datasets.
        
        Returns:
            Dictionary mapping dataset name to file path
        """
        print("Generating LogiGuard datasets...")
        
        files = {}
        files['inventory'] = self.generate_inventory()
        files['shipments'] = self.generate_shipments()
        files['disruptions'] = self.generate_disruptions()
        files['suppliers'] = self.generate_suppliers()
        
        print(f"\nAll datasets generated successfully in {self.data_dir}")
        return files
    
    def generate_inventory(self, num_records: int = 500) -> Path:
        """Generate inventory.csv with 500 records.
        
        Args:
            num_records: Number of inventory records to generate
        
        Returns:
            Path to generated CSV file
        """
        print(f"Generating inventory.csv ({num_records} records)...")
        
        records = []
        for i in range(num_records):
            sku = f"SKU-{i+1:05d}"
            category = random.choice(self.CATEGORIES)
            region = random.choice(self.REGIONS)
            
            # Generate stock levels with some violations
            safety_stock = random.randint(50, 200)
            reorder_point = int(safety_stock * 1.5)
            
            # 5% of items below safety stock (edge case)
            if random.random() < 0.05:
                current_stock = random.randint(0, safety_stock - 1)
            else:
                current_stock = random.randint(safety_stock, safety_stock * 3)
            
            record = {
                'SKU': sku,
                'Product_Name': f"{category} Product {i+1}",
                'Category': category,
                'Current_Stock': current_stock,
                'Safety_Stock': safety_stock,
                'Reorder_Point': reorder_point,
                'Unit_Cost': round(random.uniform(10, 500), 2),
                'Region': region,
                'Last_Updated': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        filepath = self.data_dir / 'inventory.csv'
        df.to_csv(filepath, index=False)
        print(f"  ✓ Created {filepath} ({len(df)} records)")
        
        return filepath
    
    def generate_shipments(self, num_records: int = 300) -> Path:
        """Generate shipments.csv with 300 records.
        
        Args:
            num_records: Number of shipment records to generate
        
        Returns:
            Path to generated CSV file
        """
        print(f"Generating shipments.csv ({num_records} records)...")
        
        records = []
        for i in range(num_records):
            shipment_id = f"SHIP-{i+1:06d}"
            sku = f"SKU-{random.randint(1, 500):05d}"
            
            # Select origin and destination regions
            origin_region = random.choice(self.REGIONS)
            dest_region = random.choice([r for r in self.REGIONS if r != origin_region])
            
            origin_port = random.choice(self.PORTS[origin_region])
            dest_port = random.choice(self.PORTS[dest_region])
            
            ship_date = datetime.now() - timedelta(days=random.randint(1, 60))
            expected_delivery = ship_date + timedelta(days=random.randint(14, 45))
            
            # Determine status
            status = random.choice(self.SHIPMENT_STATUSES)
            
            # 10% of shipments have NULL Adjusted_Delivery (edge case)
            if status == "Delayed" and random.random() < 0.10:
                adjusted_delivery = None  # NULL value for uncertainty testing
            elif status == "Delayed":
                adjusted_delivery = (expected_delivery + timedelta(days=random.randint(3, 15))).strftime('%Y-%m-%d')
            else:
                adjusted_delivery = expected_delivery.strftime('%Y-%m-%d')
            
            record = {
                'Shipment_ID': shipment_id,
                'SKU': sku,
                'Quantity': random.randint(100, 5000),
                'Origin_Port': origin_port,
                'Destination_Port': dest_port,
                'Ship_Date': ship_date.strftime('%Y-%m-%d'),
                'Expected_Delivery': expected_delivery.strftime('%Y-%m-%d'),
                'Adjusted_Delivery': adjusted_delivery,
                'Status': status,
                'Carrier': random.choice(self.CARRIERS),
                'Region': dest_region
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        filepath = self.data_dir / 'shipments.csv'
        df.to_csv(filepath, index=False)
        print(f"  ✓ Created {filepath} ({len(df)} records)")
        
        return filepath
    
    def generate_disruptions(self, num_records: int = 50) -> Path:
        """Generate disruptions.csv with 50 records.
        
        Args:
            num_records: Number of disruption records to generate
        
        Returns:
            Path to generated CSV file
        """
        print(f"Generating disruptions.csv ({num_records} records)...")
        
        records = []
        for i in range(num_records):
            disruption_id = f"DISR-{i+1:04d}"
            region = random.choice(self.REGIONS)
            disruption_type = random.choice(self.DISRUPTION_TYPES)
            
            # 3 active disruptions with severity >= 4 (edge case)
            if i < 3:
                severity = random.randint(4, 5)
                start_date = datetime.now() - timedelta(days=random.randint(1, 7))
                expected_resolution = (start_date + timedelta(days=random.randint(5, 20))).strftime('%Y-%m-%d')
            else:
                severity = random.randint(1, 5)
                start_date = datetime.now() - timedelta(days=random.randint(30, 180))
                # Some resolved, some with expected resolution
                if random.random() < 0.5:
                    expected_resolution = (start_date + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                else:
                    expected_resolution = None
            
            # Select affected ports from the region
            affected_ports = random.sample(self.PORTS[region], k=random.randint(1, 3))
            
            record = {
                'Disruption_ID': disruption_id,
                'Region': region,
                'Type': disruption_type,
                'Severity': severity,
                'Start_Date': start_date.strftime('%Y-%m-%d'),
                'Expected_Resolution': expected_resolution,
                'Affected_Ports': ', '.join(affected_ports),
                'Description': f"{disruption_type} affecting {region} region"
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        filepath = self.data_dir / 'disruptions.csv'
        df.to_csv(filepath, index=False)
        print(f"  ✓ Created {filepath} ({len(df)} records)")
        
        return filepath
    
    def generate_suppliers(self, num_records: int = 100) -> Path:
        """Generate suppliers.csv with 100 records.
        
        Args:
            num_records: Number of supplier records to generate
        
        Returns:
            Path to generated CSV file
        """
        print(f"Generating suppliers.csv ({num_records} records)...")
        
        records = []
        
        # Track SKUs to ensure some have no alternatives (edge case)
        sku_supplier_count = {}
        
        for i in range(num_records):
            supplier_id = f"SUP-{i+1:04d}"
            region = random.choice(self.REGIONS)
            
            # Each supplier supplies 3-10 SKUs
            num_skus = random.randint(3, 10)
            skus = [f"SKU-{random.randint(1, 500):05d}" for _ in range(num_skus)]
            
            # Track SKU supplier count
            for sku in skus:
                sku_supplier_count[sku] = sku_supplier_count.get(sku, 0) + 1
            
            # Backup region (optional)
            backup_region = random.choice([r for r in self.REGIONS if r != region]) if random.random() < 0.6 else None
            
            record = {
                'Supplier_ID': supplier_id,
                'Supplier_Name': f"Supplier {i+1} Corp",
                'Region': region,
                'SKUs_Supplied': ', '.join(skus),
                'Avg_Lead_Time_Days': random.randint(7, 60),
                'Reliability_Score': round(random.uniform(70, 99), 1),
                'Contact_Email': f"supplier{i+1}@example.com",
                'Backup_Region': backup_region
            }
            records.append(record)
        
        # Ensure 2 SKUs have only one supplier (edge case)
        single_supplier_skus = [sku for sku, count in sku_supplier_count.items() if count == 1]
        if len(single_supplier_skus) < 2:
            # Force create 2 SKUs with single supplier
            for j in range(2):
                sku = f"SKU-{490+j:05d}"
                records[j]['SKUs_Supplied'] = sku
        
        df = pd.DataFrame(records)
        filepath = self.data_dir / 'suppliers.csv'
        df.to_csv(filepath, index=False)
        print(f"  ✓ Created {filepath} ({len(df)} records)")
        
        return filepath


def main():
    """Main function to generate all datasets."""
    generator = DataGenerator()
    generator.generate_all()


if __name__ == "__main__":
    main()

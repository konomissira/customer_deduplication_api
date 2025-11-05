#!/usr/bin/env python3
"""
Script to seed the database with sample customer data
Usage: python data/seed_data.py
"""
import json
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import Customer, SourceSystem


def clear_existing_data(db):
    """Clear all existing customer data"""
    count = db.query(Customer).delete()
    db.commit()
    print(f"Cleared {count} existing customer records")


def load_sample_data(db, clear_first=True):
    """Load sample customer data from JSON file"""
    if clear_first:
        clear_existing_data(db)
    
    # Read sample data file
    json_file = os.path.join(os.path.dirname(__file__), 'sample_customers.json')
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Create customer records
    customers = []
    for customer_data in data['customers']:
        customer = Customer(
            customer_id=customer_data['customer_id'],
            name=customer_data['name'],
            email=customer_data['email'],
            source=SourceSystem(customer_data['source'])
        )
        customers.append(customer)
    
    # Bulk insert
    db.add_all(customers)
    db.commit()
    
    print(f"Successfully loaded {len(customers)} customer records")
    
    # Show summary statistics
    print("\n--- Summary ---")
    print(f"Total records: {len(customers)}")
    
    # Count by source
    salesforce_count = sum(1 for c in customers if c.source == SourceSystem.SALESFORCE)
    hubspot_count = sum(1 for c in customers if c.source == SourceSystem.HUBSPOT)
    internal_count = sum(1 for c in customers if c.source == SourceSystem.INTERNAL)
    
    print(f"Salesforce: {salesforce_count} records")
    print(f"HubSpot: {hubspot_count} records")
    print(f"Internal: {internal_count} records")
    
    # Show unique customer IDs
    unique_ids = set(c.customer_id for c in customers)
    print(f"\nUnique customers: {len(unique_ids)}")
    print(f"Duplicates: {len(customers) - len(unique_ids)}")
    print(f"Unique customer IDs: {sorted(unique_ids)}")


def main():
    """Main function"""
    print("=" * 50)
    print("Customer Deduplication API - Data Seeding")
    print("=" * 50)
    print()
    
    # Create database session
    db = SessionLocal()
    
    try:
        load_sample_data(db, clear_first=True)
        print("\n✅ Database seeded successfully!")
        print("\nYou can now:")
        print("1. Visit http://localhost:8000/docs to test the API")
        print("2. Try GET /api/v1/deduplication/analyze")
        print("3. Try GET /api/v1/deduplication/compare-sources")
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
from sqlalchemy.orm import Session
from app.models import Customer, SourceSystem
from app.schemas import CustomerCreate, DeduplicationResult, SourceComparisonResult
from typing import List


class CustomerService:
    """Service class for customer deduplication operations"""

    @staticmethod
    def create_customer(db: Session, customer_data: CustomerCreate) -> Customer:
        """Create a new customer record"""
        customer = Customer(
            customer_id=customer_data.customer_id,
            name=customer_data.name,
            email=customer_data.email,
            source=customer_data.source
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def bulk_create_customers(db: Session, customers_data: List[CustomerCreate]) -> List[Customer]:
        """Bulk create customer records"""
        customers = [
            Customer(
                customer_id=customer_data.customer_id,
                name=customer_data.name,
                email=customer_data.email,
                source=customer_data.source
            )
            for customer_data in customers_data
        ]
        db.add_all(customers)
        db.commit()
        return customers

    @staticmethod
    def get_all_customers(db: Session) -> List[Customer]:
        """Get all customer records"""
        return db.query(Customer).all()

    @staticmethod
    def get_customers_by_source(db: Session, source: SourceSystem) -> List[Customer]:
        """Get customers from a specific source"""
        return db.query(Customer).filter(Customer.source == source).all()

    @staticmethod
    def deduplicate_customers(db: Session) -> DeduplicationResult:
        """
        Deduplicate customers using SET UNION operation
        Returns unique customer IDs and statistics
        """
        # Get all customer records
        all_customers = db.query(Customer).all()
        
        # Extract customer_ids into a list
        all_customer_ids = [customer.customer_id for customer in all_customers]
        
        # Use SET to get unique customer IDs (Union operation in action!)
        unique_customer_ids = set(all_customer_ids)
        
        # Calculate statistics
        total_records = len(all_customer_ids)
        unique_count = len(unique_customer_ids)
        duplicates = total_records - unique_count
        
        return DeduplicationResult(
            total_records=total_records,
            unique_customers=unique_count,
            duplicates_found=duplicates,
            unique_customer_ids=sorted(list(unique_customer_ids))
        )

    @staticmethod
    def compare_sources(db: Session) -> SourceComparisonResult:
        """
        Compare customer IDs across different sources using SET operations
        - Union: all unique customers
        - Intersection: customers in all sources
        - Difference: customers unique to each source
        """
        # Get customer IDs from each source
        salesforce_customers = db.query(Customer.customer_id).filter(
            Customer.source == SourceSystem.SALESFORCE
        ).all()
        salesforce_ids = set([c.customer_id for c in salesforce_customers])
        
        hubspot_customers = db.query(Customer.customer_id).filter(
            Customer.source == SourceSystem.HUBSPOT
        ).all()
        hubspot_ids = set([c.customer_id for c in hubspot_customers])
        
        internal_customers = db.query(Customer.customer_id).filter(
            Customer.source == SourceSystem.INTERNAL
        ).all()
        internal_ids = set([c.customer_id for c in internal_customers])
        
        # SET OPERATIONS
        # Intersection: customers in ALL three sources
        in_all_sources = salesforce_ids & hubspot_ids & internal_ids
        
        # Difference: customers unique to each source
        only_salesforce = salesforce_ids - hubspot_ids - internal_ids
        only_hubspot = hubspot_ids - salesforce_ids - internal_ids
        only_internal = internal_ids - salesforce_ids - hubspot_ids
        
        return SourceComparisonResult(
            in_all_sources=sorted(list(in_all_sources)),
            only_in_salesforce=sorted(list(only_salesforce)),
            only_in_hubspot=sorted(list(only_hubspot)),
            only_in_internal=sorted(list(only_internal)),
            salesforce_count=len(salesforce_ids),
            hubspot_count=len(hubspot_ids),
            internal_count=len(internal_ids)
        )

    @staticmethod
    def clear_all_customers(db: Session) -> int:
        """Delete all customer records (for testing/reset)"""
        count = db.query(Customer).delete()
        db.commit()
        return count
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import (
    CustomerCreate,
    CustomerResponse,
    CustomerBulkUpload,
    DeduplicationResult,
    SourceComparisonResult,
    MessageResponse
)
from app.models import SourceSystem
from app.services import CustomerService

router = APIRouter(prefix="/api/v1", tags=["customers"])


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a single customer record
    """
    try:
        new_customer = CustomerService.create_customer(db, customer)
        return new_customer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create customer: {str(e)}"
        )


@router.post("/customers/bulk", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def bulk_upload_customers(
    bulk_data: CustomerBulkUpload,
    db: Session = Depends(get_db)
):
    """
    Bulk upload customer records from multiple sources
    """
    try:
        customers = CustomerService.bulk_create_customers(db, bulk_data.customers)
        return MessageResponse(
            message=f"Successfully uploaded {len(customers)} customer records",
            details={"count": len(customers)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to bulk upload customers: {str(e)}"
        )


@router.get("/customers", response_model=List[CustomerResponse])
def get_all_customers(db: Session = Depends(get_db)):
    """
    Get all customer records from all sources
    """
    customers = CustomerService.get_all_customers(db)
    return customers


@router.get("/customers/source/{source}", response_model=List[CustomerResponse])
def get_customers_by_source(
    source: SourceSystem,
    db: Session = Depends(get_db)
):
    """
    Get customers from a specific source (salesforce, hubspot, or internal)
    """
    customers = CustomerService.get_customers_by_source(db, source)
    return customers


@router.get("/deduplication/analyze", response_model=DeduplicationResult)
def analyze_deduplication(db: Session = Depends(get_db)):
    """
    Analyze customer data for duplicates using SET UNION operation
    
    Returns:
    - Total records in database
    - Unique customer count
    - Number of duplicates found
    - List of unique customer IDs
    """
    result = CustomerService.deduplicate_customers(db)
    return result


@router.get("/deduplication/compare-sources", response_model=SourceComparisonResult)
def compare_sources(db: Session = Depends(get_db)):
    """
    Compare customer IDs across different sources using SET operations
    
    Set Operations Used:
    - Intersection (&): Customers in ALL sources
    - Difference (-): Customers unique to each source
    
    Returns:
    - Customers in all three sources
    - Customers only in Salesforce
    - Customers only in HubSpot
    - Customers only in Internal database
    """
    result = CustomerService.compare_sources(db)
    return result


@router.delete("/customers", response_model=MessageResponse)
def clear_all_customers(db: Session = Depends(get_db)):
    """
    Delete all customer records (useful for testing/reset)
    """
    count = CustomerService.clear_all_customers(db)
    return MessageResponse(
        message=f"Successfully deleted all customer records",
        details={"deleted_count": count}
    )
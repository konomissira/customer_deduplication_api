from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional
from app.models import SourceSystem


# Request schemas
class CustomerCreate(BaseModel):
    """Schema for creating a new customer"""
    customer_id: int = Field(..., description="Customer ID from source system")
    name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    email: EmailStr = Field(..., description="Customer email address")
    source: SourceSystem = Field(..., description="Source system")


class CustomerBulkUpload(BaseModel):
    """Schema for bulk uploading customers"""
    customers: List[CustomerCreate]


# Response schemas
class CustomerResponse(BaseModel):
    """Schema for customer response"""
    id: int
    customer_id: int
    name: str
    email: str
    source: SourceSystem
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeduplicationResult(BaseModel):
    """Schema for deduplication results"""
    total_records: int
    unique_customers: int
    duplicates_found: int
    unique_customer_ids: List[int]


class SourceComparisonResult(BaseModel):
    """Schema for comparing customers across sources"""
    in_all_sources: List[int]
    only_in_salesforce: List[int]
    only_in_hubspot: List[int]
    only_in_internal: List[int]
    salesforce_count: int
    hubspot_count: int
    internal_count: int


class MessageResponse(BaseModel):
    """Schema for simple message responses"""
    message: str
    details: Optional[dict] = None
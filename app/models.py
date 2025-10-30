from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class SourceSystem(str, enum.Enum):
    """Enum for different source systems"""
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    INTERNAL = "internal"


class Customer(Base):
    """Customer model representing customer records from various sources"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    source = Column(Enum(SourceSystem), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Customer(id={self.id}, customer_id={self.customer_id}, name={self.name}, source={self.source})>"
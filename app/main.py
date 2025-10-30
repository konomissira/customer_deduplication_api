from fastapi import FastAPI
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Customer Deduplication API",
    description="API for deduplicating customer data across multiple sources using set operations",
    version="1.0.0"
)


@app.get("/")
def read_root():
    """Root endpoint - health check"""
    return {
        "message": "Customer Deduplication API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# from fastapi import FastAPI
# from app.database import engine, Base, DATABASE_URL  # Add DATABASE_URL import
# import os

# # Create database tables
# Base.metadata.create_all(bind=engine)

# # Initialize FastAPI app
# app = FastAPI(
#     title="Customer Deduplication API",
#     description="API for deduplicating customer data across multiple sources using set operations",
#     version="1.0.0"
# )


# @app.get("/")
# def read_root():
#     """Root endpoint - health check"""
#     return {
#         "message": "Customer Deduplication API",
#         "status": "running",
#         "version": "1.0.0",
#         "debug_db_url": DATABASE_URL,  # DEBUG - shows the connection string
#         "debug_env": {
#             "POSTGRES_USER": os.getenv("POSTGRES_USER"),
#             "POSTGRES_DB": os.getenv("POSTGRES_DB"),
#             "POSTGRES_HOST": os.getenv("POSTGRES_HOST"),
#         }
#     }
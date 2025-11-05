import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_customers():
    """Sample customer data for testing"""
    return {
        "customers": [
            {"customer_id": 101, "name": "John Doe", "email": "john@example.com", "source": "salesforce"},
            {"customer_id": 102, "name": "Jane Smith", "email": "jane@example.com", "source": "salesforce"},
            {"customer_id": 103, "name": "Bob Johnson", "email": "bob@example.com", "source": "salesforce"},
            {"customer_id": 103, "name": "Bob Johnson", "email": "bob@example.com", "source": "hubspot"},
            {"customer_id": 104, "name": "Alice Williams", "email": "alice@example.com", "source": "hubspot"},
            {"customer_id": 105, "name": "Charlie Brown", "email": "charlie@example.com", "source": "hubspot"},
            {"customer_id": 102, "name": "Jane Smith", "email": "jane@example.com", "source": "internal"},
            {"customer_id": 105, "name": "Charlie Brown", "email": "charlie@example.com", "source": "internal"},
            {"customer_id": 106, "name": "David Lee", "email": "david@example.com", "source": "internal"}
        ]
    }
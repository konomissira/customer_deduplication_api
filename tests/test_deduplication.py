import pytest
from fastapi import status


class TestHealthEndpoints:
    """Test basic health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct response"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "running"
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"


class TestCustomerCreation:
    """Test customer creation endpoints"""
    
    def test_create_single_customer(self, client):
        """Test creating a single customer"""
        customer_data = {
            "customer_id": 999,
            "name": "Test User",
            "email": "test@example.com",
            "source": "salesforce"
        }
        response = client.post("/api/v1/customers", json=customer_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["customer_id"] == 999
        assert data["name"] == "Test User"
        assert data["source"] == "salesforce"
    
    def test_bulk_upload_customers(self, client, sample_customers):
        """Test bulk uploading customers"""
        response = client.post("/api/v1/customers/bulk", json=sample_customers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "Successfully uploaded 9 customer records" in data["message"]
        assert data["details"]["count"] == 9


class TestCustomerRetrieval:
    """Test customer retrieval endpoints"""
    
    def test_get_all_customers_empty(self, client):
        """Test getting customers when database is empty"""
        response = client.get("/api/v1/customers")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_all_customers(self, client, sample_customers):
        """Test getting all customers after upload"""
        # Upload customers first
        client.post("/api/v1/customers/bulk", json=sample_customers)
        
        # Get all customers
        response = client.get("/api/v1/customers")
        assert response.status_code == status.HTTP_200_OK
        customers = response.json()
        assert len(customers) == 9
    
    def test_get_customers_by_source_salesforce(self, client, sample_customers):
        """Test getting customers from Salesforce"""
        # Upload customers first
        client.post("/api/v1/customers/bulk", json=sample_customers)
        
        # Get Salesforce customers
        response = client.get("/api/v1/customers/source/salesforce")
        assert response.status_code == status.HTTP_200_OK
        customers = response.json()
        assert len(customers) == 3
        assert all(c["source"] == "salesforce" for c in customers)
    
    def test_get_customers_by_source_hubspot(self, client, sample_customers):
        """Test getting customers from HubSpot"""
        client.post("/api/v1/customers/bulk", json=sample_customers)
        
        response = client.get("/api/v1/customers/source/hubspot")
        assert response.status_code == status.HTTP_200_OK
        customers = response.json()
        assert len(customers) == 3
        assert all(c["source"] == "hubspot" for c in customers)
    
    def test_get_customers_by_source_internal(self, client, sample_customers):
        """Test getting customers from Internal database"""
        client.post("/api/v1/customers/bulk", json=sample_customers)
        
        response = client.get("/api/v1/customers/source/internal")
        assert response.status_code == status.HTTP_200_OK
        customers = response.json()
        assert len(customers) == 3
        assert all(c["source"] == "internal" for c in customers)


class TestDeduplication:
    """Test deduplication logic using SET operations"""
    
    def test_deduplication_with_no_data(self, client):
        """Test deduplication when database is empty"""
        response = client.get("/api/v1/deduplication/analyze")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_records"] == 0
        assert data["unique_customers"] == 0
        assert data["duplicates_found"] == 0
        assert data["unique_customer_ids"] == []
    
    def test_deduplication_analysis(self, client, sample_customers):
        """Test deduplication finds correct unique customers using SET UNION"""
        # Upload customers with duplicates
        client.post("/api/v1/customers/bulk", json=sample_customers)
        
        # Analyze deduplication
        response = client.get("/api/v1/deduplication/analyze")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify results
        assert data["total_records"] == 9  # Total uploaded
        assert data["unique_customers"] == 6  # Unique after SET operation
        assert data["duplicates_found"] == 3  # 9 - 6 = 3 duplicates
        
        # Check unique customer IDs
        expected_unique_ids = [101, 102, 103, 104, 105, 106]
        assert data["unique_customer_ids"] == expected_unique_ids
    
    def test_deduplication_with_all_unique(self, client):
        """Test deduplication when all customers are unique"""
        unique_customers = {
            "customers": [
                {"customer_id": 201, "name": "User 1", "email": "user1@example.com", "source": "salesforce"},
                {"customer_id": 202, "name": "User 2", "email": "user2@example.com", "source": "hubspot"},
                {"customer_id": 203, "name": "User 3", "email": "user3@example.com", "source": "internal"}
            ]
        }
        client.post("/api/v1/customers/bulk", json=unique_customers)
        
        response = client.get("/api/v1/deduplication/analyze")
        data = response.json()
        
        assert data["total_records"] == 3
        assert data["unique_customers"] == 3
        assert data["duplicates_found"] == 0


class TestSourceComparison:
    """Test source comparison using SET operations (intersection, difference)"""
    
    def test_compare_sources_with_no_data(self, client):
        """Test source comparison when database is empty"""
        response = client.get("/api/v1/deduplication/compare-sources")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["in_all_sources"] == []
        assert data["only_in_salesforce"] == []
        assert data["only_in_hubspot"] == []
        assert data["only_in_internal"] == []
        assert data["salesforce_count"] == 0
        assert data["hubspot_count"] == 0
        assert data["internal_count"] == 0
    
    def test_compare_sources(self, client, sample_customers):
        """Test source comparison using SET INTERSECTION and DIFFERENCE"""
        # Upload customers
        client.post("/api/v1/customers/bulk", json=sample_customers)
        
        # Compare sources
        response = client.get("/api/v1/deduplication/compare-sources")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Salesforce: [101, 102, 103]
        # HubSpot: [103, 104, 105]
        # Internal: [102, 105, 106]
        
        # Intersection: None in all three sources
        assert data["in_all_sources"] == []
        
        # Difference: Unique to each source
        assert data["only_in_salesforce"] == [101]  # Only in SF
        assert data["only_in_hubspot"] == [104]     # Only in HS
        assert data["only_in_internal"] == [106]    # Only in Internal
        
        # Counts
        assert data["salesforce_count"] == 3
        assert data["hubspot_count"] == 3
        assert data["internal_count"] == 3
    
    def test_compare_sources_customer_in_all_systems(self, client):
        """Test when a customer exists in all three sources"""
        customers = {
            "customers": [
                {"customer_id": 999, "name": "Everywhere User", "email": "everywhere@example.com", "source": "salesforce"},
                {"customer_id": 999, "name": "Everywhere User", "email": "everywhere@example.com", "source": "hubspot"},
                {"customer_id": 999, "name": "Everywhere User", "email": "everywhere@example.com", "source": "internal"}
            ]
        }
        client.post("/api/v1/customers/bulk", json=customers)
        
        response = client.get("/api/v1/deduplication/compare-sources")
        data = response.json()
        
        # Customer 999 should be in all sources (SET INTERSECTION)
        assert data["in_all_sources"] == [999]
        assert data["only_in_salesforce"] == []
        assert data["only_in_hubspot"] == []
        assert data["only_in_internal"] == []


class TestDataCleanup:
    """Test data cleanup functionality"""
    
    def test_clear_all_customers(self, client, sample_customers):
        """Test clearing all customer data"""
        # Upload customers first
        client.post("/api/v1/customers/bulk", json=sample_customers)
        
        # Verify data exists
        response = client.get("/api/v1/customers")
        assert len(response.json()) == 9
        
        # Clear all data
        response = client.delete("/api/v1/customers")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Successfully deleted" in data["message"]
        assert data["details"]["deleted_count"] == 9
        
        # Verify data is gone
        response = client.get("/api/v1/customers")
        assert response.json() == []
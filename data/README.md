# Sample Data

This directory contains sample customer data for testing and demonstrating the deduplication API.

## Files

### `sample_customers.json`

JSON format sample data with 12 customer records across 3 sources:

-   **Salesforce**: 4 records (customer IDs: 101, 102, 103, 104)
-   **HubSpot**: 4 records (customer IDs: 103, 104, 105, 106)
-   **Internal**: 4 records (customer IDs: 102, 105, 107, 108)

### `sample_customers.csv`

Same data in CSV format for alternative loading methods.

### `seed_data.py`

Python script to automatically load sample data into the database.

## Data Overview

The sample data demonstrates common deduplication scenarios:

### Duplicates Across Sources

-   **Customer 102** (Jane Smith) appears in Salesforce AND Internal
-   **Customer 103** (Bob Johnson) appears in Salesforce AND HubSpot
-   **Customer 104** (Sarah Wilson) appears in Salesforce AND HubSpot
-   **Customer 105** (Alice Williams) appears in HubSpot AND Internal

### Unique Customers per Source

-   **Customer 101** (John Doe) - Only in Salesforce
-   **Customer 106** (Charlie Brown) - Only in HubSpot
-   **Customer 107** (David Lee) - Only in Internal
-   **Customer 108** (Emma Davis) - Only in Internal

### Expected Results

When analyzing this data:

-   **Total records**: 12
-   **Unique customers**: 8 (using SET UNION)
-   **Duplicates found**: 4

When comparing sources:

-   **In multiple sources**: Customers 102, 103, 104, 105
-   **Only in Salesforce**: Customer 101
-   **Only in HubSpot**: Customer 106
-   **Only in Internal**: Customers 107, 108

## Usage

### Load Sample Data into Database

**From outside the Docker container:**

```bash
docker-compose exec app python data/seed_data.py
```

**From inside the Docker container:**

```bash
docker-compose exec app bash
python data/seed_data.py
```

**Running locally (without Docker):**

```bash
python data/seed_data.py
```

### Using the API with Sample Data

After seeding, try these endpoints:

1. **View all customers**

    ```
    GET http://localhost:8000/api/v1/customers
    ```

2. **Analyze deduplication**

    ```
    GET http://localhost:8000/api/v1/deduplication/analyze
    ```

    Should return: 12 total records, 8 unique customers, 4 duplicates

3. **Compare sources**

    ```
    GET http://localhost:8000/api/v1/deduplication/compare-sources
    ```

    Shows which customers are unique to each source

4. **Get customers by source**
    ```
    GET http://localhost:8000/api/v1/customers/source/salesforce
    GET http://localhost:8000/api/v1/customers/source/hubspot
    GET http://localhost:8000/api/v1/customers/source/internal
    ```

### Clear Data

To remove all sample data:

```bash
curl -X DELETE http://localhost:8000/api/v1/customers
```

Or use the Swagger UI at http://localhost:8000/docs

# Customer Deduplication API

A production-ready REST API for deduplicating customer data across multiple sources using Python set operations.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-16%20passed-success.svg)](tests/)

## 📋 Overview

This project demonstrates efficient data deduplication techniques for merging customer records from multiple CRM systems (Salesforce, HubSpot, Internal Database) using **Python set operations**. Built as a real-world example of how data structures and algorithms solve practical data engineering problems.

### The Problem

When customer data exists across multiple systems, you end up with:

-   **Duplicate records** - Same customer appears in multiple databases
-   **Inconsistent counts** - Total records ≠ unique customers
-   **Reconciliation challenges** - Which system has the "truth"?

### The Solution

Using **set operations** (union, intersection, difference) to efficiently:

-   Deduplicate millions of records in O(n) time
-   Find customers across all systems (intersection)
-   Identify system-specific customers (difference)
-   Generate reconciliation reports instantly

## 🚀 Features

-   **Bulk Upload**: Import customer data from multiple sources via REST API
-   **Deduplication Analysis**: Find unique customers using SET UNION operation
-   **Source Comparison**: Compare customers across sources using SET INTERSECTION and DIFFERENCE
-   **Source Filtering**: Query customers from specific CRM systems
-   **Data Cleanup**: Clear and reset data for testing
-   **Auto-generated API Docs**: Interactive Swagger UI and ReDoc
-   **Comprehensive Tests**: 16 pytest unit tests covering all functionality
-   **Sample Data**: Pre-built datasets for quick demos

## 🛠️ Tech Stack

| Technology                  | Purpose                                  |
| --------------------------- | ---------------------------------------- |
| **Python 3.11**             | Programming language                     |
| **FastAPI**                 | Modern, high-performance web framework   |
| **PostgreSQL 15**           | Relational database for data persistence |
| **SQLAlchemy**              | ORM for database operations              |
| **Pydantic**                | Data validation and serialization        |
| **Docker & Docker Compose** | Containerization and orchestration       |
| **pytest**                  | Testing framework                        |
| **Uvicorn**                 | ASGI web server                          |

## 📦 Installation

### Prerequisites

-   [Docker Desktop](https://www.docker.com/products/docker-desktop) installed
-   [Git](https://git-scm.com/) installed
-   Port 8000 and 5432 available

### Setup

1. **Clone the repository**

    ```bash
    git clone https://github.com/konomissira/customer_deduplication_api.git
    cd customer_deduplication_api
    ```

2. **Create environment file**

    ```bash
    cp .env.example .env
    ```

3. **Build and start containers**

    ```bash
    docker compose up --build
    ```

4. **Load sample data** (optional)

    ```bash
    docker compose exec app python data/seed_data.py
    ```

5. **Access the API**
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - API Root: http://localhost:8000

## 📖 Usage

### Quick Start with Sample Data

```bash
# Start the application
docker compose up -d

# Load sample data (12 customer records with duplicates)
docker compose exec app python data/seed_data.py

# Access API documentation
open http://localhost:8000/docs
```

### API Endpoints

#### 1. Upload Customers

**POST** `/api/v1/customers/bulk`

```bash
curl -X POST "http://localhost:8000/api/v1/customers/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [
      {"customer_id": 101, "name": "John Doe", "email": "john@example.com", "source": "salesforce"},
      {"customer_id": 102, "name": "Jane Smith", "email": "jane@example.com", "source": "hubspot"}
    ]
  }'
```

#### 2. Analyze Deduplication (SET UNION)

**GET** `/api/v1/deduplication/analyze`

```bash
curl http://localhost:8000/api/v1/deduplication/analyze
```

**Response:**

```json
{
    "total_records": 12,
    "unique_customers": 8,
    "duplicates_found": 4,
    "unique_customer_ids": [101, 102, 103, 104, 105, 106, 107, 108]
}
```

#### 3. Compare Sources (SET INTERSECTION & DIFFERENCE)

**GET** `/api/v1/deduplication/compare-sources`

```bash
curl http://localhost:8000/api/v1/deduplication/compare-sources
```

**Response:**

```json
{
    "in_all_sources": [],
    "only_in_salesforce": [101],
    "only_in_hubspot": [106],
    "only_in_internal": [107, 108],
    "salesforce_count": 4,
    "hubspot_count": 4,
    "internal_count": 4
}
```

#### 4. Get Customers by Source

```bash
# Get Salesforce customers
curl http://localhost:8000/api/v1/customers/source/salesforce

# Get HubSpot customers
curl http://localhost:8000/api/v1/customers/source/hubspot

# Get Internal customers
curl http://localhost:8000/api/v1/customers/source/internal
```

#### 5. Clear All Data

**DELETE** `/api/v1/customers`

```bash
curl -X DELETE http://localhost:8000/api/v1/customers
```

## 🧮 Set Operations Explained

This project demonstrates three key set operations:

### 1. Union (`|`) - Deduplication

```python
salesforce = {101, 102, 103}
hubspot = {103, 104, 105}

all_unique = salesforce | hubspot  # {101, 102, 103, 104, 105}
```

**Result:** 5 unique customers from 6 total records

### 2. Intersection (`&`) - Find Overlaps

```python
in_both = salesforce & hubspot  # {103}
```

**Result:** Customer 103 exists in both systems

### 3. Difference (`-`) - Find Unique Records

```python
only_salesforce = salesforce - hubspot  # {101, 102}
only_hubspot = hubspot - salesforce  # {104, 105}
```

**Result:** Customers unique to each system

## 🧪 Testing

Run the test suite with pytest:

```bash
# Run all tests
docker compose exec app pytest

# Run with verbose output
docker compose exec app pytest -v

# Run specific test class
docker compose exec app pytest tests/test_deduplication.py::TestDeduplication -v

# Run locally (without Docker)
pytest -v
```

**Test Coverage:**

-   ✅ Health check endpoints
-   ✅ Customer creation (single and bulk)
-   ✅ Data retrieval and filtering
-   ✅ Deduplication logic (SET UNION)
-   ✅ Source comparison (SET INTERSECTION & DIFFERENCE)
-   ✅ Data cleanup operations

**Result:** 16 tests passing ✅

## 📁 Project Structure

```
customer_deduplication_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database connection and session management
│   ├── models.py            # SQLAlchemy models (Customer table)
│   ├── schemas.py           # Pydantic schemas for validation
│   ├── services.py          # Business logic (set operations)
│   └── api/
│       ├── __init__.py
│       └── endpoints.py     # API route definitions
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures and configuration
│   └── test_deduplication.py  # Unit tests
├── data/
│   ├── README.md            # Sample data documentation
│   ├── sample_customers.json
│   ├── sample_customers.csv
│   └── seed_data.py         # Script to load sample data
├── .env.example             # Environment variables template
├── .gitignore
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container definition
├── pytest.ini               # Pytest configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Development

### Local Development (Without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # To activate .venv on Mac
.venv\Scripts\activate   # To activate .venv on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_USER=dedup_user
export POSTGRES_PASSWORD=dedup_password
export POSTGRES_DB=deduplication_db

# Run the application
uvicorn app.main:app --reload
```

### Stopping the Application

```bash
# Stop containers
docker compose down

# Stop and remove volumes (clears database)
docker compose down -v
```

## 📊 Performance

Set operations provide excellent performance characteristics:

| Operation          | Time Complexity | Space Complexity |
| ------------------ | --------------- | ---------------- |
| Union (`\|`)       | O(n + m)        | O(n + m)         |
| Intersection (`&`) | O(min(n, m))    | O(min(n, m))     |
| Difference (`-`)   | O(n)            | O(n)             |

Where n and m are the sizes of the input sets.

**Example:** Deduplicating 1 million records across 3 sources takes ~0.1 seconds using set operations, compared to hours with nested loops.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

Built as part of a data engineering portfolio project demonstrating:

-   Clean architecture and design patterns
-   RESTful API development with FastAPI
-   Database modeling with SQLAlchemy
-   Docker containerization
-   Test-driven development with pytest
-   Professional Git workflow with feature branches
-   Comprehensive documentation

## 🔗 Related Resources

-   [FastAPI Documentation](https://fastapi.tiangolo.com/)
-   [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
-   [Docker Documentation](https://docs.docker.com/)
-   [Python Set Operations](https://docs.python.org/3/tutorial/datastructures.html#sets)

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using Python, FastAPI, and PostgreSQL**

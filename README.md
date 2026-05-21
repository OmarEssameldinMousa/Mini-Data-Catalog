# 📚 Mini Data Catalog - Comprehensive Documentation

> **Welcome to the comprehensive documentation for the Mini Data Catalog!**  
> This guide covers architecture, setup instructions, service breakdowns, API usage, environment configurations, and development guidelines.

## 🌟 Overview

The **Mini Data Catalog** is a lightweight, microservices-based platform designed to manage data metadata, enforce schema validation, track data lineage, and handle automated data ingestion. Built using modern asynchronous Python (FastAPI) and a modular containerized architecture, it provides a robust foundation for modern data governance.

---

## 🏛️ System Architecture

The platform is designed around a microservices architecture, communicating primarily through REST APIs and persisting state in a unified PostgreSQL instance. 

To ensure domain isolation, each service operates against its own distinct logical database within the shared PostgreSQL server (e.g., `registry_db`, `validator_db`, `lineage_db`, `ingestion_db`). An Nginx API Gateway routes incoming traffic to the appropriate backend service.

```mermaid
graph TD
    Client([Client / Data Consumer]) --> Gateway[Nginx API Gateway :80]
    
    Gateway -->|/api/registry/*| Registry[Registry Service :8001]
    Gateway -->|/api/validator/*| Validator[Validator Service :8002]
    Gateway -->|/api/lineage/*| Lineage[Lineage Service :8003]
    Gateway -->|/api/ingestion/*| Ingestion[Ingestion Service :8004]

    Registry --> DB[(PostgreSQL :5432)]
    Validator --> DB
    Lineage --> DB
    Ingestion --> DB
    
    %% Inter-service communications
    Registry -.->|HTTP Request| Validator
    Ingestion -.->|HTTP Request| Registry
    Ingestion -.->|HTTP Request| Validator
```

---

## 🧩 Deep Dive: Microservices Breakdown

### 1. Registry Service (`:8001` | `/api/registry/`)
The core source of truth for metadata management. It handles the registration, versioning, and querying of data assets (e.g., datasets, tables, models).
- **Core Endpoints:**
  - `POST /datasets/` - Register a new dataset.
  - `GET /datasets/` - List and filter datasets.
  - `GET /datasets/{id}` - Fetch details of a specific dataset.
  - `POST /datasets/{id}/versions` - Add a new version of a dataset. When a version is added, the Registry service synchronously validates the schema against the Validator service.

### 2. Validator Service (`:8002` | `/api/validator/`)
Responsible for schema and data quality validation. It acts as an independent rules engine that other services (like Registry and Ingestion) can query to ensure incoming data conforms to expected formats.
- **Core Endpoints:**
  - `POST /schemas/` - Define new data schemas.
  - `POST /validation/` - Validate data payload against a specific schema.

### 3. Lineage Service (`:8003` | `/api/lineage/`)
Tracks relationships, origins, and the flow of data assets. It uses a graph-like model (nodes and edges) to represent how datasets are derived from one another, enabling impact analysis and troubleshooting.
- **Core Endpoints:**
  - `POST /edges/` - Create a lineage edge (e.g., Dataset A -> Dataset B).
  - `GET /edges/{dataset_id}` - Retrieve upstream and downstream dependencies for a dataset to prevent cyclical dependencies.

### 4. Ingestion Service (`:8004` | `/api/ingestion/`)
Handles the automated pulling, processing, and ingestion of metadata from external systems or pipelines into the catalog.
- **Core Endpoints:**
  - `POST /jobs/` - Submit an ingestion job.
  - `GET /jobs/{job_id}` - Check the status of a background ingestion task.

---

## 🛠️ Technology Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11)
* **Database:** PostgreSQL 16 (with `asyncpg` and `alembic` for migrations)
* **Containerization:** Docker & Docker Compose
* **API Gateway:** Nginx 1.27
* **HTTP Client:** `httpx` for asynchronous inter-service communication

---

## 📂 Project Structure

```text
mini-data-catalog/
├── .env                    # Global environment variables
├── docker-compose.yaml     # Infrastructure orchestration
├── infra/                  # Database init scripts
├── nginx/                  # Nginx configuration (API Gateway routing)
├── scripts/                # Utility scripts (e.g. merge_openapi.py)
└── services/               # Microservices root
    ├── ingestion/          # Ingestion Service source code
    ├── lineage/            # Lineage Service source code
    ├── registry/           # Registry Service source code
    └── validator/          # Validator Service source code
```

---

## ⚙️ Environment Configuration

The application requires a `.env` file at the root of the project to run successfully. This file defines database credentials and inter-service communication URLs.

**Example `.env` structure:**
```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_MULTIPLE_DATABASES=registry_db,validator_db,lineage_db,ingestion_db

# Registry Service
REGISTRY_SERVICE_NAME=registry_service
REGISTRY_DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/registry_db
REGISTRY_VALIDATOR_URL=http://validator:8000

# Validator Service
VALIDATOR_SERVICE_NAME=validator_service
VALIDATOR_DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/validator_db

# (Similar blocks exist for Lineage and Ingestion services)
```

---

## 🚀 Setup & Installation

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Running Locally

1. **Clone the repository and configure environment variables:**
   Ensure your `.env` file is present in the root directory.

2. **Build and start all services:**
   ```bash
   docker compose up --build -d
   ```

3. **Verify the services are healthy:**
   ```bash
   docker compose ps
   ```
   You should see all `nginx`, `postgres`, `registry`, `validator`, `lineage`, and `ingestion` services running and marked as healthy.

4. **Tearing Down:**
   To stop and remove all containers, networks, and volumes:
   ```bash
   docker compose down -v
   ```

---

## 🌐 Unified API Documentation

To make development and integration easier, Nginx hosts a centralized Swagger UI page that combines the endpoints from all four microservices.

**Access the UI here:**
👉 `http://localhost/docs/`

**How it works:**
Whenever the services are updated, you can regenerate the unified `merged_openapi.json` file by running:
```bash
python3 scripts/merge_openapi.py
```
This script queries each microservice, aggregates their `openapi.json` schemas, and overwrites `nginx/merged_openapi.json` to keep your frontend documentation perfectly in sync with your backend code.

---

## 📖 Extended Example Workflow

### 1. Check Service Health
**Request:**
```bash
curl -X GET http://localhost/api/registry/health
```
**Response:**
```json
{
  "status": "ok",
  "service": "registry_service",
  "version": "0.1.0"
}
```

### 2. Create a Dataset
**Request:**
```bash
curl -X POST http://localhost/api/registry/datasets/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "customer_transactions",
    "description": "Daily customer transaction logs",
    "owner": "finance_team",
    "data_format": "PARQUET",
    "status": "ACTIVE"
  }'
```
**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "customer_transactions",
  "description": "Daily customer transaction logs",
  "owner": "finance_team",
  "data_format": "PARQUET",
  "status": "ACTIVE",
  "created_at": "2026-05-21T15:30:00Z",
  "updated_at": "2026-05-21T15:30:00Z"
}
```

---

## 🔧 Development & Best Practices

- **Inter-service Communication:** Services communicate via asynchronous HTTP requests using `httpx`. Explicit timeouts are configured on all `httpx.AsyncClient` objects to ensure resilience and prevent hanging connections.
- **Correlation IDs:** A custom middleware handles `X-Correlation-ID` injection for request tracing. When the Ingestion service makes a request to the Registry service, the Correlation ID is passed via headers, ensuring logs can be traced horizontally across the entire ecosystem.
- **Exception Handling:** Each service implements a domain-driven exception handling pattern using FastAPI's `@app.exception_handler`. Custom exceptions (e.g. `DatasetNotFound`, `CycleDetected`) are caught globally and translated into standardized JSON responses (e.g., `404 Not Found`, `400 Bad Request`).
- **Database Migrations:** Use Alembic to manage schema changes in PostgreSQL. Because each service has its own logical database, you must run migrations individually per service.

---

Developed by Omar Essam as a personal project .

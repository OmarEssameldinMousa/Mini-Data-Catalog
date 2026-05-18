# 🚧 Mini Data Catalog (Under Construction) 🚧

> **⚠️ WORK IN PROGRESS**  
> This project is currently under active development. Features are incomplete, and the codebase is subject to rapid, breaking changes. It is not yet ready for production use.

## Overview
A lightweight, microservices-based data catalog designed to manage metadata, validate schemas, track data lineage, and handle data ingestion. Built with modern, asynchronous Python and modular containerized architecture.

## 🏗️ Architecture Stack
* **Framework:** FastAPI (Python 3.11)
* **Database:** PostgreSQL (with Asyncpg & Alembic)
* **Containerization:** Docker & Docker Compose
* **API Gateway / Reverse Proxy:** Nginx

## 🧩 Microservices
The platform is broken down into four distinct microservices:
1. **Registry Service (`:8001`):** Core metadata management and entity registration.
2. **Validator Service (`:8002`):** Schema and data quality validation.
3. **Lineage Service (`:8003`):** Tracks relationships, origins, and flows of data assets.
4. **Ingestion Service (`:8004`):** Handles automated pulling and ingestion of metadata from external sources.

## 🚀 Getting Started (Development)

To spin up the infrastructure and all microservices locally:

```bash
# Clone the repository
git clone https://github.com/yourusername/mini-data-catalog.git
cd mini-data-catalog

# Build and start all services via Docker Compose
docker compose up --build -d
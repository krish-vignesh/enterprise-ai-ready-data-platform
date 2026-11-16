
# 🚀 Enterprise AI-Ready Data Platform

> **Building an enterprise AI platform from first principles with open-source technologies and a future path to Azure.**

This project explores how enterprise data is ingested, stored, secured, processed, governed, and prepared for AI workloads.

The goal is not simply to make an application work. It is to understand **why each component exists, how it works, and how it fits into the larger architecture**.

---

## 🎯 Project Vision

Enterprise data comes from many systems and formats. Before it can reliably support analytics, machine learning, or generative AI, it needs a dependable data foundation.

The platform is being developed around this flow:

```text
Enterprise Data Sources
          |
          v
     Data Ingestion
          |
          v
     Object Storage <------> PostgreSQL
          |
          v
  Distributed Processing
      (Apache Spark)
          |
          v
   Curated / AI-Ready Data
          |
          +------> Analytics
          |
          +------> Machine Learning
          |
          +------> Generative AI / RAG
```

This is the **long-term direction** of the platform. Some layers are implemented; others remain on the roadmap.

---

## 🏗️ Architecture and Current Capabilities

### 🔐 Identity, Authentication and Company Access

- **Keycloak** handles external identity operations such as login, credentials, and token issuance.
- **FastAPI** validates JWT access tokens and resolves the Keycloak identity to an internal platform user.
- **PostgreSQL** stores internal users, companies, and company memberships.
- A user can belong to multiple companies, or to no company.
- Company membership determines access to company-owned resources.

The relationship is:

```text
Keycloak Identity
       |
       v
Internal Platform User
       |
       v
Company Membership
       |
       +------> Company A
       |
       +------> Company B
```

**Company roles:** `OWNER`, `ADMIN`, and `MEMBER`.

| Permission | OWNER | ADMIN | MEMBER |
|---|:---:|:---:|:---:|
| View company resources | ✅ | ✅ | ✅ |
| Create source systems | ✅ | ✅ | ✅ |
| Create datasets | ✅ | ✅ | ❌ |
| Upload documents | ✅ | ✅ | ✅ |
| Manage members and roles | ✅ | ❌ | ❌ |
| Delete company | ✅ | ❌ | ❌ |

Authorization is enforced by the backend using company-membership and resource-ownership checks. The API does not rely on a client-provided company ID as proof of access.

### 🏢 Company Registration

The company registration workflow creates:

1. A company record.
2. A membership record for the creating user.
3. The creator's initial role as `OWNER`.

The company and initial membership are created as one logical registration operation.

### 🔌 Source System Catalog

A source system represents an external business system connected to a company, such as a CRM.

Implemented endpoints:

- `POST /api/v1/companies/{company_id}/source-systems` — create a source system.
- `GET /api/v1/companies/{company_id}/source-systems` — list source systems for a company.
- `GET /api/v1/source-systems/{source_id}` — retrieve an individual source system.

The individual-resource endpoint resolves the source system and checks access against the company that owns it.

### 📥 Document Ingestion Foundation

The platform includes document-ingestion workflows using company and dataset ownership.

Current design includes:

- Single-file and batch upload workflows.
- File validation and document metadata.
- SHA-256-based duplicate detection.
- MinIO object storage.
- PostgreSQL metadata and ingestion state.
- Bronze-ingestion foundations for downstream processing.

**Batch API decisions:**

- Maximum of 10 files per batch.
- Maximum aggregate batch size of 100 MiB.
- Sequential file processing.
- Continue processing after an individual file failure.
- Reject the entire batch if the referenced dataset is missing.
- Completed batch requests return HTTP `200`.

---

## 🧰 Technology Stack

### Backend and API

- Python
- FastAPI
- Uvicorn
- Pydantic

### Database and Persistence

- PostgreSQL
- SQLAlchemy (async)
- Alembic

### Identity and Security

- Keycloak
- OAuth 2.0 / OpenID Connect
- JWT and JWKS validation
- Company-membership authorization

### Storage and Processing

- MinIO
- Apache Spark 4.2.0
- PySpark
- Hadoop S3A

### Infrastructure and Developer Tools

- Docker
- Docker Compose
- `uv`
- Ruff
- pytest

The broader roadmap includes Delta Lake, data quality, metadata, lineage, governance, and Azure services.

---

## ⚡ Distributed Processing with Spark

A local Dockerized Spark cluster has been built and connected to MinIO through Hadoop S3A.

```text
                 Spark Master
                      |
             +--------+--------+
             |                 |
             v                 v
        Worker 1           Worker 2
             |                 |
             +--------+--------+
                      |
                      v
                 Spark Driver
                      |
                      v
             Distributed Execution
                      |
                      v
                    MinIO
```

The practical Spark pipeline:

1. Reads JSONL data from MinIO.
2. Creates a Spark DataFrame.
3. Applies a customer transformation.
4. Writes processed data in Parquet format.
5. Stores Spark event logs for later inspection.

MinIO separates application data and Spark event logs:

- `ai-data` — application and business data.
- `spark-events` — Spark execution event logs.

### Spark Interfaces

- Spark Master UI: `http://localhost:8080`
- Live Spark Application UI: `http://localhost:4040`
- Spark History Server: `http://localhost:18080`

The live application UI is available while an application is running. The History Server is used to inspect completed applications through persisted event logs.

---

## 🗂️ Repository Structure

The backend uses a layered structure. Each layer has a focused responsibility.

```text
enterprise-ai-ready-data-platform/
|
+-- backend/
|   +-- app/
|       +-- api/             # HTTP routes and endpoint handling
|       +-- config/          # Application configuration
|       +-- core/
|       |   +-- security/    # Authentication and authorization
|       +-- models/          # SQLAlchemy models
|       +-- repositories/    # Database access
|       +-- schemas/         # Pydantic request and response schemas
|       +-- services/        # Business logic and orchestration
|       +-- ingestion/       # Document parsing and ingestion
|       +-- storage/         # Object-storage integration
|       +-- spark/           # Spark sessions, jobs and transformations
|       +-- main.py          # FastAPI application entry point
|
+-- infrastructure/
|   +-- config/
|   +-- docker/
|   +-- scripts/
|
+-- experiments/             # Experiments and focused tests
+-- docs/                    # Supporting documentation
+-- docker-compose.yml
+-- pyproject.toml
+-- uv.lock
+-- README.md
```

This is a high-level guide, not an exhaustive file listing. Refer to the repository for the exact current structure.

---

## ▶️ Local Development

### Prerequisites

- Windows PowerShell or a compatible terminal.
- Docker Desktop with Docker Compose.
- Python and `uv`.
- The project's local environment configuration.

### 1. Configure environment variables

Create the local `.env` file using the settings required by the project.

**Never commit `.env`, passwords, access tokens, or other secrets.**

### 2. Start infrastructure

Run from the repository root:

```powershell
docker compose up -d
```

### 3. Start the backend

The project uses the existing `.venv-uv` environment.

From the `backend` directory:

```powershell
uv run --active uvicorn app.main:app --reload
```

Or, from the repository root:

```powershell
$env:PYTHONPATH = "$PWD\backend"
uv run --active uvicorn app.main:app --reload --app-dir backend
```

The local API is available at:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

### 4. Run code-quality checks

From the repository root:

```powershell
uv run --active ruff check .
uv run --active ruff format --check .
```

### 5. Run tests

From the repository root:

```powershell
$env:PYTHONPATH = "$PWD\backend"
uv run --active pytest
```

Use the existing project environment and keep `--active` in `uv run` commands. Avoid creating a second default `.venv`.

> Use the project's actual local configuration for environment variables, service ports, and test database settings. Do not place credentials in this README.

---

## 🧪 Validation

The following API workflows have been manually exercised through Postman during development:

- Company registration — `201 Created`.
- Source System creation — `201 Created`.
- Source System listing — `200 OK`.
- Individual Source System retrieval — `200 OK`.
- Company/resource authorization behaviour — checked during tenant-isolation testing.

Automated tests are also used for service and authorization behaviour.

These are development verification results, not a claim of production deployment or an independent security audit. Run the current test suite and quality checks before creating a new release or commit checkpoint.

---

## 🧭 Roadmap

### ✅ Implemented foundations

- Project architecture and foundational data-platform concepts.
- Docker and MinIO foundation.
- Dockerized Spark cluster and distributed processing.
- Spark-to-MinIO integration through S3A.
- Parquet output and Spark event logging.
- PostgreSQL models, repositories, and service foundations.
- Keycloak authentication and internal-user resolution.
- Company registration and membership-based authorization.
- Source System create, list, and retrieve APIs.
- Document-ingestion and batch-ingestion foundations.

### 🔜 Next engineering milestones

1. Dataset API design and implementation.
2. Dataset-level authorization and ownership checks.
3. Complete protected-upload and end-to-end security verification.
4. Consolidate linting, formatting, tests, documentation, and Git checkpoint.

### 🗺️ Planned platform layers

- Medallion architecture: Bronze, Silver, and Gold.
- Delta Lake and lakehouse capabilities.
- Data quality and validation.
- Metadata, lineage, and catalog.
- Data governance.
- AI-ready data consumption.
- Semantic enterprise data layer.
- Azure migration path.

---

## ☁️ Future Azure Direction

The current open-source stack is designed around portable architectural concepts.

| Current technology | Possible Azure direction |
|---|---|
| MinIO | Azure Data Lake Storage Gen2 |
| Apache Spark | Azure Databricks |
| PostgreSQL | Azure Database for PostgreSQL |
| Dockerized services | Azure container and orchestration services |
| Metadata and catalog concepts | Microsoft Purview / Unity Catalog concepts |

These are future architectural directions, not completed cloud migrations.

---

## 🧱 Engineering Principles

- **Architecture before code:** understand the problem before choosing a technology.
- **One file, one responsibility:** keep components focused and cohesive.
- **Inspect before changing:** understand existing code and dependencies first.
- **Security by design:** enforce identity, company membership, and resource ownership on the backend.
- **Configuration is not secrets:** inject credentials at runtime and keep them out of Git.
- **Incremental validation:** make a controlled change, test it, inspect the result, then continue.
- **Production-minded decisions:** prefer maintainable architecture over temporary workarounds.
- **Understand before automating:** every technology should solve a clearly understood problem.

The learning and implementation approach follows:

```text
Business Problem
       |
       v
Architecture
       |
       v
Technology Choice
       |
       v
Conceptual Understanding
       |
       v
Implementation
       |
       v
Testing and Validation
       |
       v
Code and Architecture Review
```

---

## 📌 Project Status

This is an actively developed local engineering platform.

Some foundations are implemented and verified through tests or API-level checks. Other components remain planned. This README intentionally distinguishes implemented functionality from the long-term architecture.

---

## 👨‍💻 Author

**Vignesh Krishna**  
MBA Business Analytics | Data Science | AI Engineering

> 💡 *Technology is temporary. Architectural thinking is permanent.*

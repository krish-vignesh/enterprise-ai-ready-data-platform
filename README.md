# 🚀 Enterprise AI-Ready Data Platform

> Building an Enterprise AI Platform from First Principles using Open-Source Technologies with a Future Azure Migration Path.

---

## 📖 Overview

This project is a long-term engineering initiative focused on designing and implementing an **Enterprise AI-Ready Data Platform** from scratch.

Unlike tutorial-based projects, this repository follows an architectural-first approach where every technology is introduced only after understanding the problem it solves.

The platform is being developed using open-source technologies while maintaining a clear conceptual migration path toward Microsoft Azure.

The project focuses on understanding how:

```text
Enterprise Data
      ↓
Data Ingestion
      ↓
Object Storage
      ↓
Distributed Processing
      ↓
Curated / AI-Ready Data
      ↓
Metadata & Governance
      ↓
Semantic Layer
      ↓
AI / ML / Generative AI
```

can work together as an enterprise platform.

---

# 🎯 Vision

The objective is not simply to build an application.

The objective is to understand:

- Enterprise Data Architecture
- Data Engineering
- AI Infrastructure
- Distributed Data Processing
- Data Lakes & Lakehouses
- Data Quality
- Metadata & Lineage
- Data Governance
- AI-Ready Data
- Machine Learning Infrastructure
- Generative AI Infrastructure
- Enterprise AI Architecture

Every architectural decision follows:

> **Business Problem → Architecture → Technology → Implementation → Validation**

The project prioritizes understanding **why** a technology exists before focusing on **how** to implement it.

---

# 🏗 Enterprise AI-Ready Data Platform

The long-term architecture is evolving toward:

```text
                         Business Systems
                                │
                                ▼
                      Operational Data Sources
                                │
                                ▼
                         Ingestion Layer
                                │
                                ▼
                         Landing / Raw Zone
                                │
                                ▼
                      Object Storage (MinIO)
                                │
                                ▼
                    Distributed Processing
                         Apache Spark
                                │
                                ▼
                    Bronze / Silver / Gold
                         Data Architecture
                                │
                                ▼
                         Delta / Lakehouse
                                │
                                ▼
                    AI-Ready Curated Data
                                │
             ┌──────────────────┼──────────────────┐
             ▼                  ▼                  ▼
         Analytics         Machine Learning   Generative AI
                                                   │
                                                   ▼
                                                  RAG
```

The architecture will evolve incrementally.

Not every component shown above has been implemented yet.

Future components such as Delta Lake, orchestration, metadata, governance, and semantic layers will be introduced in later stages.

---

# 🧠 Engineering Philosophy

This project intentionally avoids blindly using technologies.

Every module follows:

```text
1. Business Problem
        ↓
2. Architecture
        ↓
3. Technology Selection
        ↓
4. Conceptual Understanding
        ↓
5. Internal Working
        ↓
6. Implementation
        ↓
7. Validation
        ↓
8. Code Review
        ↓
9. Architecture Review
```

The goal is to understand:

> **WHY → WHAT → HOW → RUNTIME BEHAVIOR → PRODUCTION IMPLICATION**

rather than simply making code work.

---

# 🛠 Technology Stack

## Application Layer

### Frontend

- React
- Vite
- TypeScript

### Backend

- FastAPI
- Python

---

## Storage Layer

### Object Storage

- MinIO
- S3-compatible object storage interface

MinIO currently acts as the local object-storage foundation of the platform.

Business data is stored under locations such as:

```text
s3a://ai-data/
```

Spark event logs are stored separately:

```text
s3a://spark-events/
```

---

## Distributed Processing

### Apache Spark

Current Spark version:

```text
Apache Spark 4.2.0
```

Runtime:

```text
Java 21
Python 3.12
PySpark
```

Spark is used for:

- distributed data processing
- structured data reading
- transformations
- partitioned execution
- Parquet generation
- large-scale data preparation

The project focuses on understanding Spark at an **AI Engineer / AI Architecture level**, rather than becoming a Spark specialist.

---

## Spark Storage Integration

Spark communicates with MinIO through Hadoop's:

```text
S3A
```

interface.

The platform uses:

```text
s3a://
```

to access object storage from Spark.

---

## Table / Lakehouse Layer

### Planned

- Delta Lake
- Lakehouse architecture
- ACID transactions
- Schema enforcement
- Schema evolution
- Time Travel
- Incremental processing

Delta Lake is part of the next stage of the project and is **not yet the completed storage layer**.

---

## Infrastructure

- Docker
- Docker Compose
- Custom Spark Docker image
- Local multi-container Spark cluster

---

## Future Platform Components

The following technologies are part of the broader roadmap and will be introduced when their architectural purpose becomes relevant:

- PostgreSQL
- Airflow
- OpenMetadata
- MLflow
- Delta Lake
- Governance / Catalog systems
- Semantic technologies
- Azure services

They should not be considered completed components of the current implementation.

---

# ☁️ Azure Migration Strategy

The project is intentionally designed around portable architectural concepts.

| Current / Open-Source Component | Potential Azure Direction |
|---|---|
| MinIO | Azure Data Lake Storage Gen2 |
| Apache Spark | Azure Databricks |
| Docker / Docker Compose | Azure container / orchestration services |
| OpenMetadata | Microsoft Purview / Unity Catalog concepts |
| Local analytics layer | Power BI / Azure analytics services |

These mappings represent a **future migration direction**, not a claim that the current local implementation has already been migrated to Azure.

The objective is to understand the architecture independently of a specific cloud provider.

---

# 📂 Repository Structure

Current repository structure:

```text
enterprise-ai-ready-data-platform/
│
├── .env
├── docker-compose.yml
├── README.md
├── .gitignore
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── config/
│   │   ├── core/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │
│   │   ├── spark/
│   │   │   ├── __init__.py
│   │   │   ├── io/
│   │   │   │   ├── reader.py
│   │   │   │   └── writer.py
│   │   │   ├── jobs/
│   │   │   │   └── customer_pipeline.py
│   │   │   ├── session.py
│   │   │   └── transformations/
│   │   │       └── customer.py
│   │   │
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── parsers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── excel.py
│   │   │   │   ├── pdf.py
│   │   │   │   ├── pdf_tables.py
│   │   │   │   └── document.py
│   │   │   └── spark_adapter.py
│   │   │
│   │   ├── storage/
│   │   └── utils/
│   │
│   └── requirements.txt
│
├── infrastructure/
│   ├── config/
│   │   └── spark/
│   │       └── spark-defaults.conf
│   │
│   ├── docker/
│   │   └── spark/
│   │       └── Dockerfile
│   │
│   └── scripts/
│       └── run-spark-job.ps1
│
├── experiments/
│   ├── minio/
│   ├── spark/
│   └── ingestion/
│       ├── data/
│       ├── test_spark_adapter.py
│       ├── test_excel_to_spark.py
│       └── test_pdf_table_to_spark.py
│
├── data/
├── frontend/
├── docs/
└── assets/
```

---

# 🗄️ Storage Architecture

The current local platform uses MinIO as its S3-compatible object-storage layer.

Conceptually:

```text
                 MinIO
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
    ai-data/             spark-events/
        │                     │
        │                     │
 Business Data         Spark Event Logs
        │                     │
        ▼                     ▼
    Spark Jobs          History Server
```

These are intentionally separate concerns.

### `ai-data`

Contains application / business data used by the data platform.

Example:

```text
s3a://ai-data/spark_scaling_customers/
```

### `spark-events`

Contains Spark execution event logs.

Example:

```text
s3a://spark-events/
```

These logs are consumed by the Spark History Server.

---

# ⚡ Spark Distributed Processing Architecture

Sprint 2 established a working local distributed Spark environment.

Architecture:

```text
                    ┌─────────────────────┐
                    │    Spark Master     │
                    │       :7077         │
                    │       :8080 UI      │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
             Spark Worker 1       Spark Worker 2
                    │                     │
                    └──────────┬──────────┘
                               │
                         Spark Driver
                            :4040
                               │
                       ┌───────┴────────┐
                       ▼                ▼
                    MinIO        Spark Event Logs
                   :9000               │
                       │                ▼
                       │        Spark History Server
                       │              :18080
                       ▼
                  Data Storage
```

---

# 🐳 Dockerized Spark Environment

The project uses a custom Spark image:

```text
enterprise-spark:4.2.0
```

The image contains:

- Ubuntu 24.04
- Java 21
- Python 3.12
- Apache Spark 4.2.0
- PySpark runtime
- Hadoop AWS integration
- AWS SDK dependencies
- required Python packages

The same Spark image is reused across the Spark services.

This keeps the runtime consistent between:

- Spark Master
- Spark Workers
- Spark Driver
- Spark History Server

---

# ⚙️ Spark Configuration

The canonical Spark configuration is:

```text
infrastructure/config/spark/spark-defaults.conf
```

Current resource configuration:

```properties
spark.driver.memory=2g
spark.executor.memory=2g
spark.executor.cores=4
spark.cores.max=8
```

Event logging:

```properties
spark.eventLog.enabled=true
spark.eventLog.dir=s3a://spark-events/
```

S3A / MinIO configuration:

```properties
spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem
spark.hadoop.fs.s3a.endpoint=http://minio:9000
spark.hadoop.fs.s3a.path.style.access=true
spark.hadoop.fs.s3a.connection.ssl.enabled=false
```

The configuration is intentionally centralized.

---

# 🔐 Configuration vs Secrets

The project separates:

### Configuration

Stored in:

```text
spark-defaults.conf
```

Contains:

- Spark resources
- event logging
- S3A implementation
- MinIO endpoint
- storage behavior

### Secrets

Credentials are injected at runtime.

Local development uses:

```text
.env
```

The project does not place credentials inside:

- source code
- Dockerfile
- `spark-defaults.conf`
- documentation
- Git commits

A production deployment should use a dedicated secret-management mechanism.

---

# 🚀 Spark Job

The current practical Spark pipeline is:

```text
MinIO
  │
  ▼
JSONL Input
  │
  ▼
Spark Reader
  │
  ▼
Spark DataFrame
  │
  ▼
Customer Transformation
  │
  ▼
Distributed Processing
  │
  ▼
Parquet Output
  │
  ▼
MinIO
```

Input:

```text
s3a://ai-data/spark_scaling_customers/spark_scaling_customers.jsonl
```

Transformation:

A customer spending category is generated from:

```text
total_spend
```

Rules:

```text
total_spend < 3000
        → Low

3000 <= total_spend <= 6000
        → Medium

total_spend > 6000
        → High
```

Output:

```text
s3a://ai-data/processed/customers/
```

---

# 🧩 Spark Execution Model

The practical implementation demonstrated:

```text
Spark Application
        │
        ▼
      Driver
        │
        ▼
   Spark Master
        │
   ┌────┴────┐
   ▼         ▼
Worker 1   Worker 2
   │         │
   ▼         ▼
Executor   Executor
   │         │
   └────┬────┘
        ▼
      Tasks
        │
        ▼
    Partitions
```

The successful runs demonstrated:

- 2 executors
- 4 cores per executor
- 2 GiB memory per executor
- 8 processing tasks/partitions
- tasks distributed across the workers

This demonstrated actual distributed execution rather than a single local Spark process.

---

# 📊 Spark UI and Observability

The platform has three important Spark interfaces.

| Port | UI | Purpose |
|---|---|---|
| `8080` | Spark Master UI | Cluster and worker overview |
| `4040` | Spark Application UI | Live running application |
| `18080` | Spark History Server | Completed applications |

### Spark Application UI

```text
http://localhost:4040
```

This represents a currently running application.

It disappears after the application stops.

### Spark History Server

```text
http://localhost:18080
```

This persists application history because Spark event logs are stored in MinIO.

### Spark Master UI

```text
http://localhost:8080
```

This provides the cluster-level view.

---

# 🕒 Spark Event Logging

Spark event logging is enabled using:

```properties
spark.eventLog.enabled=true
```

Events are persisted to:

```text
s3a://spark-events/
```

The workflow is:

```text
Spark Application
        │
        ▼
Execution Events
        │
        ▼
MinIO
        │
        ▼
s3a://spark-events/
        │
        ▼
Spark History Server
        │
        ▼
localhost:18080
```

This allows completed Spark applications to be inspected after they have stopped.

---

# 🛠️ Important Engineering Refactor

An important Sprint 2 improvement was the removal of duplicated S3A configuration.

### Previous approach

```text
s3a.conf
    │
    ▼
run-spark-job.ps1
    │
    ▼
--conf spark.hadoop....
    │
    ▼
Spark
```

This duplicated Spark configuration responsibility.

### Final approach

```text
spark-defaults.conf
        │
        ▼
     Spark
        │
        ▼
      S3A
        │
        ▼
      MinIO
```

The PowerShell runner now focuses on:

- loading credentials
- validating the Spark job
- executing `spark-submit`

The old:

```text
s3a.conf
```

was removed after confirming that no project references remained.

---

# 🧱 History Server Architecture

The History Server uses the same canonical Spark configuration.

The Spark configuration directory is bind-mounted into the History Server:

```text
Host
│
└── infrastructure/config/spark/
            │
            │ bind mount
            ▼
Container
│
└── /opt/spark/conf/
```

This allows the History Server to use:

```text
spark-defaults.conf
```

without mounting the entire repository.

---

# 🐛 Troubleshooting Highlights

Sprint 2 included several real implementation problems.

## Python / Py4J

Encountered:

```text
ModuleNotFoundError: No module named 'py4j'
```

Lesson:

PySpark depends on the Python/Java integration layer and the runtime environment must contain the correct dependencies.

---

## Java / JAVA_HOME

Encountered a Java runtime configuration issue:

```text
Java not found
JAVA_HOME environment variable is not set
```

The Spark runtime was configured with:

```text
Java 21
```

and:

```text
JAVA_HOME
```

was configured appropriately.

---

## Docker / Spark Image Build

The custom Spark image required downloading the Spark distribution and supporting dependencies.

The image/build process was relatively large and required troubleshooting during development.

The final image was successfully built and used by the Spark cluster.

---

## History Server S3A Failure

The History Server initially produced an S3A access error involving:

```text
InvalidAccessKeyId
HTTP 403
```

The Spark jobs themselves could already write event logs successfully.

The issue was that the History Server did not have the project's active S3A configuration.

The clean fix was:

```text
./infrastructure/config/spark
            ↓
     /opt/spark/conf
```

using a Docker bind mount.

After the change, the History Server successfully parsed event logs from:

```text
s3a://spark-events/
```

---

# ✅ Sprint 2 Validation

The final Spark run successfully demonstrated:

```text
Spark 4.2.0
      ↓
Spark Master
      ↓
2 Executors
      ↓
8 Tasks
      ↓
MinIO Input
      ↓
Transformation
      ↓
Parquet Output
      ↓
Event Log
      ↓
Spark History Server
```

Latest validated application:

```text
app-20260925134441-0002
```

The application successfully:

- connected to the Spark Master
- registered both executors
- read data from MinIO
- processed 8 tasks
- wrote Parquet output
- wrote Spark event logs
- committed the output
- exited with code `0`

The Spark History Server successfully displayed completed applications.

---

# 🎓 Learning Outcome — Sprint 2

Sprint 2 was not about becoming a Spark specialist.

The primary goal was to understand:

```text
Driver
Master
Worker
Executor
Partition
Task
Job
Stage
DataFrame
Transformation
Action
Object Storage
S3A
Event Logging
History Server
```

The most important mental model developed was:

```text
Data
 ↓
Object Storage
 ↓
Spark
 ↓
Distributed Processing
 ↓
Curated Output
 ↓
Observability
```

This establishes the distributed-processing foundation required for the later AI-ready data platform layers.

---

# 🗺️ Project Roadmap

## ✅ Sprint 0 — Planning & Architecture

Completed:

- Project planning
- Architecture design
- UI prototype
- Technology selection

---

## ✅ Sprint 1 — Theory / Foundations

Completed:

- Enterprise Data Architecture
- OLTP vs OLAP
- Data Warehouse
- Data Lake
- Object Storage
- ETL vs ELT
- Data Ingestion
- RDBMS
- NoSQL
- MinIO
- Enterprise AI Architecture
- Distributed processing fundamentals

---

## ✅ Sprint 2 — Spark Distributed Processing

Completed:

- Apache Spark fundamentals
- Spark 4.2.0
- Custom Spark Docker image
- Dockerized Spark cluster
- Spark Master
- Two Spark Workers
- Spark Driver
- Spark executors
- DataFrames
- Partitions
- Tasks
- Distributed execution
- Spark → MinIO integration
- S3A
- Parquet output
- Spark event logging
- Spark History Server
- Spark configuration centralization
- Configuration refactoring
- Runtime secret separation
- Troubleshooting and validation

---

## 🔜 Sprint 3 — Medallion Architecture + Lakehouse

Planned focus:

- Why Medallion Architecture exists
- Bronze layer
- Silver layer
- Gold layer
- Raw vs cleaned vs curated data
- Data lifecycle
- Provenance
- Reprocessing
- Incremental processing
- Idempotency
- Delta Lake
- ACID transactions
- Schema enforcement
- Schema evolution
- Time Travel
- Lakehouse architecture
- Spark + Delta integration

The objective is to transform the current Spark pipeline into a more structured enterprise data lifecycle.

---

## 🔜 Sprint 4 — Data Quality

Planned:

- Data validation
- Schema validation
- Data profiling
- Missing values
- Invalid records
- Quality rules
- Quality checkpoints
- Failure handling
- Data quality reporting

---

## 🔜 Sprint 5 — Metadata, Lineage & Governance

Planned:

- Metadata
- Technical metadata
- Business metadata
- Data lineage
- Data catalog
- Governance
- Data ownership
- Data discovery
- OpenMetadata
- Enterprise catalog concepts

---

## 🔜 Sprint 6 — AI-Ready Data

Planned:

- AI-ready datasets
- Feature engineering
- Analytics
- Machine Learning pipelines
- Generative AI data preparation
- RAG data preparation
- AI consumption layer

---

## 🔜 Future — Semantic Enterprise Layer

Planned future architecture:

```text
Taxonomy
   ↓
Ontology
   ↓
Semantic Model
   ↓
Semantic Graph
   ↓
AI Reasoning / Applications
```

This layer is intended to move the platform beyond simply storing and processing data toward understanding relationships and meaning across enterprise data.

---

# 🤖 Relationship to AI / RAG

The platform is being developed as a foundation for downstream AI systems.

A separate RAG project is also being developed around:

- document ingestion
- chunking
- embeddings
- vector retrieval
- sparse retrieval
- BM25
- reranking
- OpenSearch
- Chroma
- RAG evaluation
- LangChain
- LangGraph

The Enterprise AI-Ready Data Platform and RAG system should remain conceptually separated.

The platform prepares reliable, structured, governed and AI-ready data.

AI / RAG systems consume that data.

Conceptually:

```text
Enterprise Data Platform
          │
          ▼
     AI-Ready Data
          │
     ┌────┴─────┐
     ▼          ▼
    ML         RAG
     │          │
     ▼          ▼
 Predictions  Generative AI
```

---

# ☁️ Long-Term Vision

The platform is intended to evolve toward a production-inspired enterprise architecture capable of supporting:

- Azure Databricks
- Azure Data Lake Storage
- Microsoft Fabric
- Enterprise Data Governance
- Machine Learning Infrastructure
- Generative AI Infrastructure
- RAG Systems
- Semantic Enterprise Data
- Production AI workloads

The local open-source architecture is intentionally used to understand the underlying engineering principles before moving toward managed cloud services.

---

# 🎯 Current Project Status

| Area | Status |
|---|---|
| Project Planning | ✅ Complete |
| Architecture Foundation | ✅ Complete |
| Sprint 1 Theory | ✅ Complete |
| MinIO Foundation | ✅ Complete |
| Docker Foundation | ✅ Complete |
| Spark Cluster | ✅ Complete |
| Distributed Spark Processing | ✅ Complete |
| Spark → MinIO | ✅ Complete |
| Spark Event Logging | ✅ Complete |
| Spark History Server | ✅ Complete |
| Spark Configuration Refactor | ✅ Complete |
| Sprint 2 | ✅ Complete |
| Medallion Architecture | 🔜 Next |
| Delta Lake | 🔜 Planned |
| Data Quality | 🔜 Planned |
| Metadata / Lineage | 🔜 Planned |
| Governance | 🔜 Planned |
| AI-Ready Data Layer | 🔜 Planned |
| Semantic Layer | 🔜 Future |
| Azure Migration | 🔜 Future |

---

# 🧭 Current Position

The platform has now moved from:

```text
THEORY
  ↓
PRACTICAL INFRASTRUCTURE
  ↓
DISTRIBUTED PROCESSING
```

The next architectural transition is:

```text
Distributed Processing
        ↓
Medallion Architecture
        ↓
Lakehouse / Delta
        ↓
Data Quality
        ↓
Metadata & Governance
        ↓
AI-Ready Data
        ↓
Semantic Enterprise Data
        ↓
AI / ML / Generative AI
```

---

# 🚀 Next Immediate Step

The next sprint should begin by answering:

> **"We can already store raw data and process it with Spark. Why isn't that enough for an enterprise AI-ready data platform?"**

From there, the project will introduce:

```text
BRONZE
  ↓
SILVER
  ↓
GOLD
```

before implementing the next layer.

The goal is to understand the architecture first and implement it incrementally.

---

# 🤝 Engineering Principles

This project follows several principles:

### 1. Architecture Before Code

Understand the problem before selecting the technology.

### 2. One Responsibility Per Component

Avoid unnecessary coupling and giant modules.

### 3. Configuration Is Not Secrets

Keep configuration and credentials separate.

### 4. Validate Incrementally

Make one architectural change, test it, inspect the result, then continue.

### 5. Production Thinking

Prefer clean architectural solutions over temporary hacks.

### 6. Understand Before Automating

Automation tools should solve a clearly understood problem.

### 7. AI Engineer Perspective

Understand enough of every layer to reason about the complete AI system without unnecessarily becoming a specialist in every underlying technology.

---

# 📚 Learning Philosophy

The project is being developed as a structured engineering learning journey.

The goal is not:

> "Use as many technologies as possible."

The goal is:

> **Understand why each component exists, how it works, how it fits into the architecture, and how it enables enterprise AI.**

Every new technology should answer:

```text
What problem does it solve?
        ↓
Why do we need it?
        ↓
Where does it fit?
        ↓
How does it work?
        ↓
How do we implement it?
        ↓
How do we validate it?
        ↓
How would it evolve in production?
```

---

# 👨‍💻 Author

**Vignesh Krishna**

MBA Business Analytics | Data Science | AI Engineering

---

> **"Technology is temporary. Architectural thinking is permanent."**
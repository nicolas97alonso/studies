---
tags: [databricks, moc]
aliases: [Databricks Index, Databricks Hub]
---

# Databricks Study Notes

Map of Content for all Databricks notes.

> [!info] Exam: Databricks Certified Data Engineer Associate
> Topics marked `exam-priority` in their frontmatter are high-frequency exam topics. Start there.

---

## Exam Priority Topics (Study These First)

| Priority | Topic | File |
|:---|:---|:---|
| 🔴 Critical | Delta Lake — ACID, transaction log, MERGE, time travel, VACUUM | [[db-delta]] |
| 🔴 Critical | Delta Live Tables — expectations, pipeline modes, medallion | [[db-dlt]] |
| 🔴 Critical | Auto Loader — cloudFiles, schema evolution, checkpointing | [[db-autoloader]] |
| 🔴 Critical | Cluster Types — Job vs All-Purpose, access modes for UC | [[db-databricks]] |
| 🔴 Critical | Unity Catalog — 3-level namespace, privileges, table types | [[db-unity-catalog]] |
| 🟠 High | Spark Architecture — jobs/stages/tasks, shuffles, lazy eval | [[db-spark]] |
| 🟠 High | SQL — managed vs external tables, views, DESCRIBE commands | [[db-sparksql]] |
| 🟠 High | Workflows — job types, repair run, task dependencies | [[db-workflows]] |
| 🟡 Medium | Structured Streaming — output modes, triggers, watermarks | [[db-streaming]] |

---

## All Notes

### Core Architecture
- [[db-databricks]] — Clusters, control/data plane, DBU pricing
- [[db-spark]] — Spark internals, execution model, AQE, caching

### Storage & Ingestion
- [[db-delta]] — Delta Lake internals, ACID, MERGE, time travel, OPTIMIZE
- [[db-autoloader]] — Incremental file ingestion with cloudFiles
- [[db-datalake]] — ADLS Gen2, authentication methods
- [[db-dbfs]] — DBFS *(legacy — pre-Unity Catalog reference)*

### Pipelines & Orchestration
- [[db-dlt]] — Delta Live Tables, expectations, medallion architecture
- [[db-streaming]] — Structured Streaming concepts (underlying DLT)
- [[db-workflows]] — Jobs, task types, scheduling, repair runs

### SQL & Governance
- [[db-sparksql]] — Spark SQL, DDL, table model, write modes
- [[db-unity-catalog]] — 3-level namespace, privileges, volumes, lineage

### Development
- [[db-notebooks]] — Notebooks, magic commands, `dbutils`
- [[db-secrets]] — Secret scopes, Azure Key Vault integration

---

## Exam Topic Coverage Map

| Exam Domain | Coverage |
|:---|:---|
| Databricks Lakehouse Platform | [[db-databricks]], [[db-unity-catalog]] |
| Apache Spark concepts | [[db-spark]] |
| Delta Lake | [[db-delta]], [[db-sparksql]] |
| Incremental data processing | [[db-autoloader]], [[db-streaming]], [[db-delta]] |
| Production pipelines | [[db-dlt]], [[db-workflows]] |
| Data governance | [[db-unity-catalog]], [[db-secrets]] |
| Storage & access | [[db-datalake]], [[db-dbfs]] |

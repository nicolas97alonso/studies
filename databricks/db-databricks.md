---
tags: [databricks, architecture, clusters, exam-priority]
aliases: [Databricks Architecture, Clusters, DBU]
---

# Databricks Architecture & Clusters

> [!important] Exam Priority: HIGH
> Cluster types (All-Purpose vs Job), access modes for Unity Catalog, and autoscaling are frequently tested.

---

## 1. High-Level Architecture (Split-Plane)

Databricks separates management from processing:

### Control Plane *(Databricks-managed, in Databricks' cloud account)*
- Web UI, notebook authoring, dashboards
- Cluster Manager — provisions/terminates VMs
- Unity Catalog — centralized governance
- Workspace assets — notebooks, queries, code metadata

### Data Plane / Compute Plane *(where your data is processed)*

| Type | Runs in | Setup |
|:---|:---|:---|
| **Classic Compute** | Customer's cloud subscription | You manage VMs and VNet |
| **Serverless Compute** | Databricks-managed subscription | Instant, always-on, no VMs to configure |

> [!note] Two separate bills
> You pay Databricks for **DBU usage** AND your cloud provider for **VM/infrastructure costs** separately. These are two different invoices.

---

## 2. Clusters

A cluster = a set of VMs acting as a single computational unit.

### Node Roles
- **Driver Node** — maintains state, responds to user queries, distributes work to executors
- **Worker Nodes** — run Spark Executors, perform actual data processing

See [[db-spark]] for how Spark uses this topology.

---

## 3. Cluster Types (Classic Compute)

> [!important] Exam Priority: HIGH — this question appears constantly.

| Feature | All-Purpose Cluster | Job Cluster |
|:---|:---|:---|
| **Primary use** | Interactive dev & exploration | Automated production pipelines |
| **Lifecycle** | Created manually; persists until stopped | Created at job start, terminated at job end |
| **Cost** | Higher DBU rate | Lower (discounted) DBU rate |
| **Sharing** | Multiple users simultaneously | Isolated to one job run |

---

## 4. Cluster Configuration

### Node Types
- **Multi-node:** 1 Driver + N Workers — for distributed, large-scale workloads
- **Single-node:** Driver only — for small datasets, local libraries (pandas, scikit-learn), ML development

### Access Modes (Unity Catalog requirement)

| Mode | UC Support | Notes |
|:---|:---|:---|
| **Single User** | Full support | Dedicated to one user |
| **Shared** | Full support | Multiple users, secure isolation between sessions |
| **No Isolation Shared** | Partial | Legacy — no security boundary between users. Cannot use UC fine-grained access. |

> [!important] Exam trap
> To use Unity Catalog fine-grained access controls (row/column-level security), the cluster must be in **Single User** or **Shared** access mode. No Isolation Shared does not support this.

### Key Features
- **Databricks Runtime (DBR):** Core engine = Spark + optimized libraries. Use **DBR ML** for pre-installed ML frameworks (PyTorch, TensorFlow, XGBoost).
- **Autoscaling:** Set Min/Max workers; Databricks scales up/down based on load.
- **Auto-termination:** Shuts down after N minutes of inactivity. Always set this on All-Purpose clusters.
- **Cluster Policies:** Admin-defined templates restricting settings (VM sizes, max cost, timeout). Enforces compliance.

---

## 5. Cluster Pools

**Problem:** Cloud VMs take 3–7 minutes to boot.  
**Solution:** Pools maintain a set of warm, pre-allocated VMs. Cluster start time drops to seconds.

- Set **Min Idle** of 1–2 to guarantee fast startups
- Reduces costs vs always-on clusters while still being fast

---

## 6. Databricks Runtime Versions

| Runtime | Contents |
|:---|:---|
| **Databricks Runtime (DBR)** | Spark, Delta Lake, standard Python libraries |
| **DBR ML** | DBR + PyTorch, TensorFlow, scikit-learn, XGBoost |
| **DBR Photon** | DBR with Photon query engine (vectorized, faster SQL) |

> [!tip] For exam: Photon = faster SQL/Delta queries via vectorized execution. Not for arbitrary Python code.

---

## 7. Pricing & DBU Calculation

**DBU = Databricks Unit** — the billing unit for compute.

```
Total Databricks cost = Total DBUs × Price per DBU (varies by workload type and tier)
Total cloud cost      = Driver VM cost + Σ Worker VM costs (per hour)
```

### VM Type Selection

| VM Type | Best For |
|:---|:---|
| Memory Optimized | Heavy joins, shuffles, large DataFrames |
| Compute Optimized | Complex transformations, large ML inference |
| Storage Optimized | High I/O, disk-heavy operations |
| GPU Accelerated | Deep learning, image/video processing |

---

> **Always set auto-termination (20–30 min) on All-Purpose clusters. Use Job Clusters for anything schedulable.**

---

> Related: [[db-spark]] (Spark internals), [[db-workflows]] (Job Clusters in pipelines), [[db-unity-catalog]] (cluster access modes for UC)

---

## 8. Photon Engine Deep Dive

Photon is a **vectorized query engine** written in C++ that replaces the standard JVM-based Spark engine for SQL and Delta operations.

**How vectorized execution works:**
- Standard Spark: processes one row at a time through JVM bytecode
- Photon: processes a **batch of 1,000+ rows at once** using CPU SIMD instructions — like applying a formula to an entire spreadsheet column vs. one cell at a time

**What Photon accelerates:**
- SQL queries (SELECT, JOIN, GROUP BY, ORDER BY)
- Delta OPTIMIZE and data writes
- MERGE operations

**What Photon does NOT accelerate:**
- Arbitrary Python/Scala UDFs — these still go through JVM
- ML training code

> [!tip] Exam tip
> Choose Photon runtime when your workload is primarily SQL/Delta operations. If you have heavy Python UDFs, the benefit is reduced.

---

## 9. Serverless Compute vs. Classic Compute

| Feature | Classic Compute | Serverless Compute |
|:---|:---|:---|
| **VM management** | You manage VMs (size, config, VNet) | Databricks manages VMs |
| **Startup time** | 3–7 minutes (VM boot) | Seconds (pre-warmed pool) |
| **Autoscaling** | Supported but slow | Instant — scales within seconds |
| **Network** | Your VNet | Databricks-managed network |
| **Billing** | DBUs + cloud VM costs | DBUs only (VMs included) |
| **Use case** | Custom network config, compliance | Fast ad-hoc queries, notebooks |

> [!note] Serverless SQL Warehouse
> The most common exam context for serverless is **Serverless SQL Warehouses** — used for Databricks SQL (BI queries). These start instantly vs. Classic SQL Warehouses that take 2–5 minutes.

> [!tip] When the exam asks which is "faster to start": Serverless. When it asks about "custom network configuration": Classic.

---

## 10. Practice Questions

**Q1.** A data engineering team runs ad-hoc exploration during business hours and scheduled ETL overnight. Which cluster type for each?
> **Answer:** Ad-hoc exploration → **All-Purpose Cluster** (always on, interactive). Overnight ETL → **Job Clusters** (lower DBU rate, auto-terminate when done).

**Q2.** A cluster is set to "No Isolation Shared" access mode. Can it use Unity Catalog row-level security?
> **Answer:** No. Row/column-level security in Unity Catalog requires **Single User** or **Shared** access mode. No Isolation Shared has only partial UC support.

**Q3.** What is the difference between DBR and DBR ML?
> **Answer:** DBR ML includes everything in DBR plus pre-installed ML frameworks: PyTorch, TensorFlow, scikit-learn, XGBoost, and GPU drivers. Use DBR ML for machine learning workloads.

**Q4.** Your team runs SQL dashboards that need to start immediately. Which configuration should you recommend?
> **Answer:** **Serverless SQL Warehouse** — starts in seconds vs. 2–5 minutes for classic.

**Q5.** Why does Photon improve SQL query performance but not Python UDF performance?
> **Answer:** Photon is a vectorized C++ engine that processes batches of rows at the CPU level. Python UDFs run through the Python/JVM interpreter, which Photon cannot accelerate — those still execute row-by-row through Python.

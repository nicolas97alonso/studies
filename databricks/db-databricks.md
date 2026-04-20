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

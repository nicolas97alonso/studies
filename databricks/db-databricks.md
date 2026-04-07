---
tags: [databricks, architecture, clusters]
aliases: [Databricks Architecture, Clusters]
---

# Databricks Architecture & Clusters

## 1. High-Level Architecture
Databricks uses a **split-plane** architecture to separate management from processing.

### A. Control Plane
*Managed by Databricks in their own cloud account.*
- **Web UI:** Workspace management, notebook authoring, and dashboarding.
- **Compute Orchestration:** The Cluster Manager that provisions and manages VM lifecycles.
- **Unity Catalog:** Centralized data governance (security, auditing, lineage).
- **Workspace Assets:** Storage for notebooks, saved queries, and code metadata.

### B. Compute Plane (Data Plane)
*Where your data processing actually happens.*
- **Classic Compute:** Runs in the **customer's** cloud subscription. You manage the VPC/VNet and VMs.
- **Serverless Compute:** Managed by Databricks — always-on, instant resource pool, AI-autoscaled.

---

## 2. Clusters
A cluster is a set of VMs working together as a single computational unit.

### Topology
- **Driver Node:** The master node. Maintains state, responds to user queries, distributes work.
- **Worker Nodes:** Run the Spark Executors and perform the actual data processing.

> See [[db-spark]] for a deep dive into how Spark uses this topology.

---

## 3. Cluster Types (Classic Compute)

| Feature | All-Purpose Cluster | Job Cluster |
| :--- | :--- | :--- |
| **Primary Use** | Interactive analysis & development | Automated production pipelines |
| **Lifecycle** | Created manually; persistent | Created/terminated by a specific Job |
| **Cost** | Higher DBU cost | Lower (discounted) DBU cost |
| **Sharing** | Shared among multiple users | Isolated to one automated task |

---

## 4. Configuration

### Node Types
- **Multi-node:** 1 Driver + N Workers. For large-scale, parallelized workloads.
- **Single-node:** Driver only. For lightweight analytics, small datasets, or non-distributed libraries.

### Access Modes
- **Single User:** Dedicated to one individual.
- **Shared:** Multiple users with secure isolation between sessions.
- **No Isolation Shared:** Legacy mode — high performance but no security boundaries between users.

### Key Features
- **Databricks Runtime (DBR):** Core engine (Spark + optimized libraries). Use **Databricks ML** for pre-installed ML frameworks (PyTorch, TensorFlow).
- **Autoscaling:** Set a Min/Max worker count; Databricks adds/removes workers based on load.
- **Auto-termination:** Shuts down the cluster after a defined idle period to prevent runaway costs.
- **Cluster Policies:** Admin-defined templates that enforce settings (e.g., restricting VM sizes).

---

## 5. Cluster Pools
**Problem:** Cloud providers take 3–7 minutes to boot VMs.  
**Solution:** Pools maintain a small set of warm, idle VM instances. When a cluster starts, it pulls from the pool — startup drops to seconds.

Set a **Min Idle** of 1–2 VMs to guarantee instant availability.

---

## 6. Pricing & DBU Calculation
Databricks costs are measured in **DBUs (Databricks Units)**.

### Total Cost
Two separate bills:
1. **Databricks Software:** `Total DBUs × Price (based on Workload/Tier)`
2. **Cloud Infrastructure:** `Driver VM Cost + Σ Worker VM Costs`

### VM Types
| Type | Best For |
| :--- | :--- |
| Memory Optimized | Heavy joins / shuffles |
| Compute Optimized | Complex transformations |
| Storage Optimized | High I/O / caching |
| GPU Accelerated | Deep Learning |

---

> **Tip:** Always set **auto-termination** (20–30 min) on All-Purpose clusters and use **Job Clusters** for anything schedulable.

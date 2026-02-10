# Databricks Architecture & Clusters: Study Guide

## 1. Databricks High-Level Architecture
Databricks operates using a "split-plane" architecture to ensure security and scalability.

### A. The Control Plane
*Managed by Databricks in their own cloud account.*
* **Web UI:** The interface for workspace management, notebook authoring, and dashboarding.
* **Compute Orchestration:** The "Cluster Manager" that provisions and manages the lifecycle of compute resources.
* **Unity Catalog:** Centralized data governance (security, auditing, and lineage).
* **Workspace Assets:** Storage for notebooks, saved queries, and code metadata.

### B. The Compute Plane (Data Plane)
*Where your data processing actually happens.*
* **Classic Compute:** Resides in the **Customer’s Cloud Subscription**. You manage the VPC/VNet and the Virtual Machines.
* **Serverless Compute:** Resources are managed by Databricks. They are "always-on" (low idle time), utilize an instant resource pool, and are automatically configured and scaled by AI.

---

## 2. Databricks Clusters
A cluster is a set of Virtual Machines (VMs) working together as a single computational unit.

### Cluster Topology
* **Driver Node:** The master node. It maintains state, responds to user queries, and distributes work.
* **Worker Nodes:** The processing units. They run the Spark Executors and perform the actual data tasks.

---

## 3. Cluster Types (Classic Compute)

| Feature | **All-Purpose Cluster** | **Job Cluster** |
| :--- | :--- | :--- |
| **Primary Use** | Interactive analysis & development | Automated production pipelines |
| **Workflow** | Created manually; persistent | Created/terminated by a specific Job |
| **Cost** | Higher DBU cost | Lower (Discounted) DBU cost |
| **Sharing** | Shared among multiple users | Isolated to a single automated task |

---

## 4. Configuration Essentials

### Node Types
* **Multi-node:** 1 Driver + $n$ Workers. Ideal for large-scale, parallelized workloads.
* **Single-node:** 1 Driver only. Best for lightweight analytics, small data, or non-distributed libraries (e.g., standard Python/R).

### Access Modes
* **Single User:** Dedicated to one specific individual.
* **Shared:** Multiple users can run code simultaneously with secure isolation.
* **No Isolation Shared:** Legacy mode; high performance but lacks security boundaries between users.

### Advanced Features
* **Databricks Runtime (DBR):** The core engine (Spark + optimized libraries). Use **Databricks ML** for pre-installed Machine Learning frameworks (PyTorch, TensorFlow).
* **Autoscaling:** Specify a **Min** and **Max** number of workers. Databricks adds/removes workers based on real-time load.
* **Auto-termination:** Automatically shuts down the cluster after a defined period of inactivity (idle time) to prevent unnecessary costs.
* **Cluster Policies:** Admin-defined templates that enforce settings (e.g., restricting VM sizes) to control costs and complexity.

---

## 5. Cluster Pools
**The Problem:** Waiting for cloud providers to boot up VMs (usually 3–7 minutes).
**The Solution:** **Pools.**
* Pools maintain a small "warm" set of idle VM instances.
* When a cluster starts, it pulls from the pool, reducing startup time to seconds.
* You can set a "Min Idle" (e.g., 1–2 VMs) to ensure instant availability.

---

## 6. Pricing & DBU Calculation
Databricks costs are measured in **DBUs (Databricks Units)**.

### Total Cost Formula
The total cost of a cluster involves two separate bills:
1.  **Databricks Software Cost:** $(\text{Total DBUs} \times \text{Price based on Workload/Tier})$
2.  **Cloud Infrastructure Cost:** $(\text{Driver VM Cost} + \sum \text{Worker VM Costs})$

### Cost Variables
* **Workload Type:** SQL and Jobs are generally cheaper than All-Purpose.
* **VM Instance Type:** * *Memory Optimized:* For heavy joins/shuffles.
    * *Compute Optimized:* For complex transformations.
    * *Storage Optimized:* High I/O / Caching.
    * *GPU Accelerated:* Deep Learning.

---

> **Pro-Tip:** To optimize costs, always set an **Auto-termination** timeout of 20–30 minutes for All-Purpose clusters and use **Job Clusters** for anything that can be scheduled!

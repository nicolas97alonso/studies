---
tags: [databricks, spark, architecture]
aliases: [Spark Architecture, PySpark, Spark Internals]
---

# Spark Architecture & Fundamentals

## 1. Physical Infrastructure

A **Node** is a single Virtual Machine. A Spark Cluster is a group of nodes solving a problem together.

### Driver Node
The "Brain." Runs the **Driver Program**.
- **SparkSession:** The command center — translates your code into instructions, manages resources, tracks cluster state. (Replaced the old `SparkContext`; wraps it internally.)
- Decides how to split the workload (partitioning) and distributes tasks.
- Where the user interacts with the cluster.

### Worker Nodes & Executors
The "Muscle."
- **Executor:** Distributed process that does the actual work (read, write, transform).
- **Databricks restricts to 1 Executor per Worker** for performance stability (unlike standard Spark which allows multiple).
- **Slots (Cores):** Unit of parallelism. 1 Slot ≈ 1 CPU Core. This is where instructions are physically executed.

---

## 2. DataFrames

A DataFrame is a distributed table with rows, columns, and a schema.

- **Partitions:** Data is split into chunks. 1TB might become 1,000 × 1GB partitions — each slot processes one chunk in parallel.
- **Data Source:** Where data comes from (CSV, S3, ADLS, etc.).
- **Data Sink:** Where processed data is written (Delta Table, Parquet, database, etc.).

### The Spark API
Spark is called an "API" because it's a **library** (PySpark, Spark SQL) that bridges your high-level code (`.groupBy()`) to distributed JVM instructions via **Py4J** — a local bridge between Python and Java.

> This is different from a web/HTTP API. PySpark is like the buttons on a microwave; a web API is like ordering pizza online.

---

## 3. Execution Hierarchy

When you run an **Action** (`.save()`, `.collect()`, `.count()`), Spark breaks execution down:

```
Application (Notebook)
└── Job          ← triggered by each Action
    └── Stage    ← divided at Shuffle boundaries
        └── Task ← 1 task = 1 slot processing 1 partition
```

### Shuffling
Shuffling is the physical movement of data across the network between worker nodes.
- Occurs on **Wide Transformations**: `groupBy`, `join`, `sort`, `distinct`.
- Example: counting "Red" cars when some live on Node A and some on Node B — Spark must shuffle them to one place.
- **Most expensive operation in Spark.** Minimize it whenever possible.

---

## 4. Memory & Distribution

| Component | Role |
| :--- | :--- |
| **Driver** | Stores the execution plan only. Does NOT load data. Will crash with `OutOfMemoryError` if you try. |
| **Executors** | Load data into RAM, process partitions, write results. |
| **Spilling** | If an Executor's RAM fills up, Spark writes overflow to the worker's local disk to avoid crashing. |

---

## 5. Scaling

| Strategy | Description | Limit |
| :--- | :--- | :--- |
| **Vertical** | Bigger VMs (more RAM/cores) | Capped by max VM size |
| **Horizontal** | More Worker Nodes | Virtually unlimited |

### Capacity Planning Rules of Thumb
- **RAM Ratio:** Total cluster RAM ≈ **2–3× your dataset size** to avoid spilling.
- **Partition Rule:** Target **2–3 tasks per CPU core**. 100 partitions → ~35–50 cores.

### VM Type Selection
| Type | Best For |
| :--- | :--- |
| Memory Optimized | Large joins / shuffles |
| Compute Optimized | Complex transformations / ML |

---

## 6. Quick Reference

| Term | Definition |
| :--- | :--- |
| **SparkSession** | Your entry point / remote control for Spark |
| **Executor** | Worker machine where data actually lives |
| **Shuffle** | Moving data between machines — slow and expensive |
| **Partition** | A small slice of your total dataset |
| **Py4J** | Hidden bridge: Python → Spark's Java engine |
| **Slot** | One CPU core = one unit of parallel work |

---

> Related: [[db-databricks]] (cluster setup), [[db-notebooks]] (working with Spark in notebooks)

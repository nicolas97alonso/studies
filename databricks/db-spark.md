---
tags: [databricks, spark, architecture, exam-priority]
aliases: [Spark Architecture, PySpark, Spark Internals]
---

# Spark Architecture & Fundamentals

> [!important] Exam Priority: HIGH
> Spark architecture questions are common. Focus on: Driver vs Executor roles, jobs/stages/tasks, transformations vs actions, and lazy evaluation.

---

## 1. Physical Infrastructure

A **Node** is a single VM. A Spark Cluster is a group of nodes solving a problem together.

### Driver Node
The "Brain." Runs the **Driver Program**.
- **SparkSession** — the entry point. Translates your code into an execution plan, manages resources, tracks cluster state. (Replaces old `SparkContext`.)
- Decides how to split workload (partitioning) and distributes tasks.
- Stores the execution **plan only** — never loads actual data into Driver memory.

> [!warning] Exam trap: Driver memory
> Never call `.collect()` on a large DataFrame. It pulls all data to the Driver, causing `OutOfMemoryError`. Use `.show()`, `.limit()`, or write to a sink instead.

### Worker Nodes & Executors
The "Muscle."
- **Executor** — distributed process that reads, transforms, and writes data.
- **Databricks uses 1 Executor per Worker** (unlike vanilla Spark which allows multiple).
- **Slots (Cores)** — unit of parallelism. 1 slot ≈ 1 CPU core. Each slot processes one partition.

---

## 2. DataFrames & Partitions

A DataFrame is a distributed table — rows, columns, and a schema.

- **Partitions** — data is split into chunks. Each executor slot processes one partition at a time.
- Target partition size: **~200 MB**
- Default shuffle partitions: `200` — usually too many for small datasets

```python
# Check partition count
df.rdd.getNumPartitions()

# Repartition (causes a shuffle)
df = df.repartition(8)

# Coalesce (reduces partitions, no shuffle)
df = df.coalesce(4)

# Change default shuffle partitions
spark.conf.set("spark.sql.shuffle.partitions", "8")
```

---

## 3. Lazy Evaluation

Spark is **lazy** — it builds an execution plan but doesn't run anything until you call an **Action**.

### Transformations (lazy — no execution)
```python
df2 = df.filter(col("amount") > 100)    # narrow transformation
df3 = df2.groupBy("country").count()    # wide transformation (causes shuffle)
df4 = df3.join(countries_df, "country") # wide transformation
```

### Actions (eager — triggers execution)
```python
df.show()          # display rows
df.count()         # count rows
df.collect()       # pull all data to Driver (⚠️ dangerous on large data)
df.write.save()    # write to storage
df.first()         # get first row
```

> [!tip] Every Action triggers a new **Job**. Chain as many transformations as possible before calling an Action.

---

## 4. Execution Hierarchy

```
Application (your notebook/script)
└── Job             ← triggered by each Action
    └── Stage       ← divided at Shuffle boundaries
        └── Task    ← 1 task = 1 slot processing 1 partition
```

### Narrow vs Wide Transformations

| Type | Description | Stage boundary? | Examples |
|:---|:---|:---|:---|
| **Narrow** | Each partition produces exactly one output partition. No data movement. | No | `filter`, `select`, `map`, `withColumn` |
| **Wide** | Multiple input partitions needed to produce one output partition. **Shuffles data.** | Yes — new Stage | `groupBy`, `join`, `sort`, `distinct`, `repartition` |

### Shuffle
Physical movement of data across the network between worker nodes.
- Most expensive operation in Spark
- Every shuffle = new Stage in the execution plan
- Minimize shuffles: filter early, use broadcast joins for small tables

---

## 5. Caching

Cache a DataFrame in memory to avoid recomputing it multiple times.

```python
df.cache()             # lazy — caches on first Action
df.persist()           # same as cache() with default storage level

# Explicit storage levels
from pyspark import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK)  # spill to disk if RAM full

# Release cache
df.unpersist()
```

> [!tip] Cache DataFrames that are used in multiple subsequent actions (e.g., an ML training loop, or a DataFrame that feeds multiple branches).

---

## 6. Broadcast Joins

When joining a large DataFrame with a small one, **broadcast** the small table to every executor — eliminates the shuffle entirely.

```python
from pyspark.sql.functions import broadcast

result = large_df.join(broadcast(small_df), "customer_id")
```

Auto-broadcast threshold (default 10 MB):
```python
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "50m")  # increase threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")   # disable auto-broadcast
```

---

## 7. Memory & Distribution

| Component | Role |
|:---|:---|
| **Driver** | Stores execution plan only. Crashes with `OutOfMemoryError` if you call `.collect()` on large data. |
| **Executors** | Load data into RAM, process partitions, write results. |
| **Spilling** | If an Executor's RAM fills up, Spark writes overflow to worker's local disk (slow but safe). |

### Capacity Planning
- **RAM Ratio:** Total cluster RAM ≈ **2–3× your dataset size** to avoid spilling.
- **Partition Rule:** Target **2–3 tasks per CPU core**. 100 cores → 200–300 partitions.

---

## 8. Adaptive Query Execution (AQE)

AQE is enabled by default in Databricks. It re-optimizes the query plan at runtime using actual data statistics.

Key features:
- **Dynamically coalesces shuffle partitions** — merges small post-shuffle partitions automatically
- **Converts sort-merge joins to broadcast joins** if one side turns out small
- **Skew join optimization** — splits skewed partitions automatically

```python
spark.conf.set("spark.sql.adaptive.enabled", "true")  # default: true in Databricks
```

---

## 9. Quick Reference

| Term | Definition |
|:---|:---|
| **SparkSession** | Entry point for Spark — replaces SparkContext |
| **Executor** | Worker process where data actually lives and is processed |
| **Shuffle** | Moving data between machines — slow, expensive, creates stage boundary |
| **Partition** | A small slice of your total dataset |
| **Slot** | One CPU core = one unit of parallel work |
| **DAG** | Directed Acyclic Graph — Spark's visual execution plan |
| **Lazy Evaluation** | Transformations build a plan; only Actions execute it |

---

> Related: [[db-databricks]] (cluster setup), [[db-notebooks]] (SparkSession in notebooks), [[db-delta]] (Delta as a Spark data source)

---

## 10. Catalyst Optimizer & Query Plans

When you write a DataFrame transformation, Spark doesn't execute it immediately. It passes through the **Catalyst Optimizer**:

```
Your code
    ↓
Unresolved Logical Plan  (parse — check syntax)
    ↓
Resolved Logical Plan    (analyze — verify columns exist)
    ↓
Optimized Logical Plan   (optimize — push filters down, prune columns)
    ↓
Physical Plans           (multiple strategies generated)
    ↓
Selected Physical Plan   (cost model picks the best)
    ↓
Execution (Tungsten code generation)
```

**Key optimizations Catalyst does automatically:**
- **Predicate pushdown** — moves `filter()` as early as possible, before joins/aggregations
- **Column pruning** — only reads columns actually used in the query
- **Constant folding** — evaluates constant expressions at compile time

```python
# See the full plan
df.explain()              # simple physical plan
df.explain("extended")    # logical + physical plans
df.explain("formatted")   # formatted version (most readable)
df.explain("cost")        # with cost estimates
```

> [!tip] `df.explain()` is your primary debugging tool for performance issues. Look for: missing predicate pushdown, sort-merge joins where broadcast would be better, unnecessary shuffles.

---

## 11. Skewed Data

**Skew** happens when data is unevenly distributed across partitions — one partition has 10M rows while others have 100. That one executor becomes the bottleneck (the "straggler").

**How to detect skew:**
- Spark UI → Stages tab → look for one task taking 10× longer than others
- Stage summary statistics: huge difference between median and max task duration

**How to fix skew:**

```python
# AQE handles most cases automatically (enabled by default in Databricks)
# For extreme skew, use salting manually:

from pyspark.sql.functions import concat, lit, rand, floor

# Add a random salt prefix to the skewed key
df_salted = df.withColumn(
    "salted_key",
    concat(col("customer_id"), lit("_"), floor(rand() * 10).cast("string"))
)
# Then aggregate within each salt bucket and sum up afterward
```

> [!note] AQE Skew Join Optimization
> If AQE detects skewed partitions (one is 5× larger than median), it automatically splits them. This is why AQE is enabled by default in Databricks — it handles most skew silently.

---

## 12. Tuning Shuffle Partitions

The default 200 shuffle partitions is too many for small data and too few for large data.

**Rule of thumb:**
- Target **128 MB–200 MB per partition** after a shuffle
- Formula: `Total data size ÷ target partition size = number of partitions`
- Example: 10 GB data → 10,000 MB ÷ 128 MB ≈ 78 partitions

```python
# Set shuffle partitions
spark.conf.set("spark.sql.shuffle.partitions", "100")

# With AQE enabled (default), Databricks auto-coalesces small partitions
# So you can set this higher and let AQE merge small ones
```

> [!important] Exam trap
> The default `200` is almost always wrong. Too few partitions = out of memory. Too many = scheduling overhead. Always tune this for your data size.

---

## 13. Practice Questions

**Q1.** Which of the following triggers a new Stage in Spark execution?
a) `filter()` b) `withColumn()` c) `groupBy().count()` d) `select()`
> **Answer:** c — `groupBy().count()` is a wide transformation that causes a shuffle, creating a new stage boundary.

**Q2.** You call `df.cache()` and then `df.count()`. When does the data actually get cached?
> **Answer:** On the first Action after `cache()` — the `count()` call. `cache()` is lazy; it marks the DataFrame to be cached but doesn't read anything yet.

**Q3.** What is the danger of calling `df.collect()` on a large DataFrame?
> **Answer:** It pulls ALL data from all executors to the Driver node's memory. If the data exceeds Driver RAM, you get `OutOfMemoryError`. Use `.show()`, `.limit()`, or write to a sink instead.

**Q4.** You join a 500 GB table with a 15 MB lookup table. Spark uses a sort-merge join. How would you optimize this?
> **Answer:** Use a broadcast join — `large_df.join(broadcast(small_df), "key")`. Broadcasting the 15 MB table to every executor eliminates the shuffle entirely. Set `spark.sql.autoBroadcastJoinThreshold` above 15 MB if auto-broadcast isn't triggering.

**Q5.** What is the difference between `repartition(10)` and `coalesce(10)`?
> **Answer:** `repartition(10)` does a full shuffle — can both increase and decrease partitions, distributes evenly. `coalesce(10)` only merges existing partitions without a shuffle — can only reduce count, may result in uneven partitions. Use `coalesce` when reducing to avoid the shuffle cost.

**Q6.** A Spark job has 3 Actions. How many Jobs does this generate?
> **Answer:** 3 Jobs — each Action triggers one Job.

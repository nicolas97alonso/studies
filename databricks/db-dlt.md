---
tags: [databricks, dlt, delta-live-tables, pipelines, exam-priority]
aliases: [Delta Live Tables, DLT, Live Tables]
---

# Delta Live Tables (DLT)

> [!important] Exam Priority: HIGH
> DLT is a newer feature that the exam now tests heavily. Focus on: syntax differences, expectations, pipeline modes, and medallion architecture in DLT.

Delta Live Tables is a declarative ETL framework. You declare *what* the data should look like, and Databricks manages *how* to run it — dependencies, retries, ordering.

---

## 1. Core Concepts

| Concept | Meaning |
|:---|:---|
| **Pipeline** | The DLT unit — a graph of tables with their transformations |
| **Dataflow Graph** | Databricks auto-generates the DAG from your `@dlt.table` dependencies |
| **Materialized View** | Result of a query, refreshed on each pipeline run (like a refreshed view) |
| **Streaming Table** | Processes only new/changed data on each run (incremental) |

> [!tip] Materialized View vs Streaming Table
> Use **Streaming Table** when the source is append-only (e.g., new log files). Use **Materialized View** when you need to re-process all data (e.g., a complex aggregation that must account for updates).

---

## 2. DLT Syntax (Python)

```python
import dlt
from pyspark.sql.functions import col

# Streaming Table — reads incrementally from Auto Loader
@dlt.table(
  name="bronze_events",
  comment="Raw events from the landing zone"
)
def bronze_events():
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .load("abfss://raw@storage.dfs.core.windows.net/events/")
    )

# Streaming Table — reads from upstream DLT table
@dlt.table(
  name="silver_events",
  comment="Cleaned and validated events"
)
@dlt.expect_or_drop("valid_event_id", "event_id IS NOT NULL")
def silver_events():
    return (
        dlt.readStream("bronze_events")  # ← read from another DLT table
            .filter(col("status") != "test")
            .select("event_id", "user_id", "timestamp", "amount")
    )

# Materialized View — re-aggregates all data on each run
@dlt.table(
  name="gold_daily_revenue",
  comment="Aggregated daily revenue"
)
def gold_daily_revenue():
    return (
        dlt.read("silver_events")   # ← batch read from DLT table
            .groupBy("date")
            .agg({"amount": "sum"})
    )
```

---

## 3. DLT SQL Syntax

```sql
-- Streaming Table
CREATE OR REFRESH STREAMING TABLE bronze_events
COMMENT "Raw events"
AS SELECT * FROM STREAM read_files(
    'abfss://raw@storage.dfs.core.windows.net/events/',
    format => 'json'
);

-- With expectations
CREATE OR REFRESH STREAMING TABLE silver_events (
  CONSTRAINT valid_id EXPECT (event_id IS NOT NULL) ON VIOLATION DROP ROW
)
AS SELECT event_id, user_id, amount
   FROM STREAM(LIVE.bronze_events)
   WHERE status != 'test';

-- Materialized View
CREATE OR REFRESH MATERIALIZED VIEW gold_daily_revenue
AS SELECT date, SUM(amount) as revenue
   FROM LIVE.silver_events
   GROUP BY date;
```

---

## 4. Expectations (Data Quality)

> [!important] Exam Priority: HIGH
> Know all three violation modes and what happens to the data for each.

Expectations declare data quality rules. Three violation modes:

| Mode | Syntax | Behaviour |
|:---|:---|:---|
| **Warn** (default) | `@dlt.expect("name", "condition")` | Records violation in metrics, row passes through |
| **Drop Row** | `@dlt.expect_or_drop("name", "condition")` | Bad rows are silently dropped |
| **Fail pipeline** | `@dlt.expect_or_fail("name", "condition")` | Pipeline stops on any violation |

```python
# Multiple expectations at once
@dlt.expect_all({
    "valid_id": "event_id IS NOT NULL",
    "positive_amount": "amount > 0"
})

# expect_all_or_drop, expect_all_or_fail also available
@dlt.expect_all_or_drop({
    "valid_id": "event_id IS NOT NULL",
    "positive_amount": "amount > 0"
})
```

```sql
-- SQL expectations
CREATE OR REFRESH STREAMING TABLE silver_events (
  CONSTRAINT valid_id    EXPECT (event_id IS NOT NULL)  ON VIOLATION DROP ROW,
  CONSTRAINT pos_amount  EXPECT (amount > 0)             ON VIOLATION WARN,
  CONSTRAINT no_test     EXPECT (status != 'test')       ON VIOLATION FAIL UPDATE
)
```

---

## 5. Pipeline Modes

| Mode | What it does | When to use |
|:---|:---|:---|
| **Triggered** | Runs once, processes all available data, stops | Scheduled batch pipelines |
| **Continuous** | Runs indefinitely, processes data as it arrives | Near-real-time pipelines (latency < 1 min) |

```json
// Pipeline settings
{
  "pipeline_mode": "TRIGGERED",    // or "CONTINUOUS"
  "continuous": false
}
```

---

## 6. Development vs. Production Mode

| Feature | Development | Production |
|:---|:---|:---|
| **Cluster reuse** | Cluster stays alive between runs | New cluster each run |
| **Retries on failure** | No automatic retries | Automatic retries |
| **Best for** | Interactive debugging | Scheduled, reliable runs |

---

## 7. Medallion Architecture in DLT

The standard pattern for data quality layers:

```
Landing Zone (cloud storage)
        ↓
🥉 Bronze (raw, unmodified ingestion)
   — streaming table from Auto Loader
   — preserves original data exactly
        ↓
🥈 Silver (cleaned, deduplicated, validated)
   — apply expectations
   — parse types, remove test data
        ↓
🥇 Gold (aggregated, business-ready)
   — materialized views for reporting
   — joined dimension tables
```

```python
# Bronze — raw ingestion
@dlt.table(name="bronze_orders")
def bronze():
    return spark.readStream.format("cloudFiles")...

# Silver — clean
@dlt.table(name="silver_orders")
@dlt.expect_or_drop("valid_order_id", "order_id IS NOT NULL")
def silver():
    return dlt.readStream("bronze_orders").select(...)

# Gold — aggregate
@dlt.table(name="gold_revenue")
def gold():
    return dlt.read("silver_orders").groupBy("date").agg(...)
```

---

## 8. Monitoring & Event Log

DLT writes pipeline events to an internal event log accessible via SQL:

```sql
-- Query pipeline event log
SELECT * FROM event_log('<pipeline-id>')
WHERE event_type = 'flow_progress';

-- Check expectation violations
SELECT
  details:flow_progress:data_quality:dropped_records,
  details:flow_progress:data_quality:expectations
FROM event_log('<pipeline-id>')
WHERE event_type = 'flow_progress';
```

---

> Related: [[db-delta]] (Delta tables DLT writes to), [[db-autoloader]] (ingestion in DLT bronze layer), [[db-streaming]] (Structured Streaming underlying concepts), [[db-workflows]] (scheduling DLT pipelines)

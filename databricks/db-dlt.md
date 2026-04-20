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

---

## 9. APPLY CHANGES INTO (Change Data Capture)

> [!important] Exam Priority: HIGH
> `APPLY CHANGES INTO` is the DLT way to handle CDC streams (SCD Type 1 and Type 2). Know the syntax and the difference between the two types.

DLT provides first-class support for applying Change Data Capture (CDC) from sources like Kafka, Kinesis, or Debezium.

### SCD Type 1 (Upsert — keep only the latest version)

```python
import dlt
from pyspark.sql.functions import col, expr

@dlt.table(name="bronze_customers_cdc")
def bronze_customers_cdc():
    return spark.readStream.format("cloudFiles")...

dlt.apply_changes(
    target   = "silver_customers",
    source   = "bronze_customers_cdc",
    keys     = ["customer_id"],
    sequence_by = col("updated_at"),
    apply_as_deletes = expr("op = 'DELETE'"),
    except_column_list = ["op", "_rescued_data"]
)
```

### SCD Type 2 (Historical — keep all versions)

```python
dlt.apply_changes(
    target   = "silver_customers_history",
    source   = "bronze_customers_cdc",
    keys     = ["customer_id"],
    sequence_by = col("updated_at"),
    apply_as_deletes = expr("op = 'DELETE'"),
    stored_as_scd_type = 2          # ← this is the only difference
)
```

SCD Type 2 automatically adds columns:

| Column | Description |
|:---|:---|
| `__START_AT` | When this version became active |
| `__END_AT` | When this version was superseded (`null` = current active row) |

```sql
-- SQL equivalent
CREATE OR REFRESH STREAMING TABLE silver_customers;

APPLY CHANGES INTO silver_customers
FROM STREAM(LIVE.bronze_customers_cdc)
KEYS (customer_id)
SEQUENCE BY updated_at
APPLY AS DELETE WHEN op = 'DELETE'
IGNORE NULL UPDATES;
```

> [!tip] SCD Type 1 vs Type 2
> **Type 1:** You only care about current state. Updates overwrite. Simpler, smaller table.
> **Type 2:** You need full history. Every change creates a new row. Essential for auditing and point-in-time analysis.

---

## 10. DLT Table vs. DLT View

> [!note] Exam distinction

| Type | Stored? | Queryable outside pipeline? | Use for |
|:---|:---|:---|:---|
| `@dlt.table` | Yes — physical Delta table | Yes | Data consumers need to read it |
| `@dlt.view` | No — virtual, computed each run | No | Intermediate transformations within the pipeline |

```python
# View — intermediate, not stored
@dlt.view(name="filtered_events")
def filtered_events():
    return dlt.read("bronze_events").filter(col("status") != "test")

# Table — stored as Delta, readable from outside
@dlt.table(name="silver_events")
def silver_events():
    return dlt.read("filtered_events").select(...)
```

> [!tip] Use views for intermediate steps that don't need to be exposed to consumers. This reduces storage and compute costs.

---

## 11. Practice Questions

**Q1.** A DLT pipeline has `@dlt.expect_or_fail("positive_amount", "amount > 0")`. A batch arrives with 5 rows having `amount = -1`. What happens?
> **Answer:** The entire pipeline run **fails** (stops). `expect_or_fail` causes pipeline failure on ANY violation.

**Q2.** What is the difference between `dlt.read()` and `dlt.readStream()` in a DLT pipeline?
> **Answer:** `dlt.read()` performs a batch read (full snapshot) — use for Materialized Views. `dlt.readStream()` performs an incremental read (only new data since last run) — use for Streaming Tables.

**Q3.** You want a DLT pipeline to process data as it arrives with < 1 minute latency. Which pipeline mode?
> **Answer:** **Continuous** mode. Triggered mode runs once and stops; Continuous mode runs indefinitely.

**Q4.** In SCD Type 2 with `APPLY CHANGES INTO`, what does `__END_AT` contain for the current active row?
> **Answer:** `null`. A null `__END_AT` means this is the current active version. When the row is updated, `__END_AT` is set to the sequence value of the update, and a new row is inserted with `__END_AT = null`.

**Q5.** What is the `sequence_by` parameter in `apply_changes` used for?
> **Answer:** It specifies which column determines the order of changes — which row is "newer." DLT uses this to correctly apply updates and deletes even when events arrive out of order.

**Q6.** How does cluster behavior differ between DLT Development and Production mode?
> **Answer:** **Development:** cluster stays alive between runs (fast iteration, no retries on failure). **Production:** new cluster per run, automatic retries on failure, guarantees a clean environment.

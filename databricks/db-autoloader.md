---
tags: [databricks, autoloader, streaming, ingestion, exam-priority]
aliases: [Auto Loader, CloudFiles, Incremental Ingestion]
---

# Auto Loader

> [!important] Exam Priority: HIGH
> Auto Loader is one of the most tested ingestion topics. Understand *why* it exists, how it differs from `spark.read`, and its two discovery modes.

Auto Loader is Databricks' solution for **incrementally ingesting new files** from cloud storage into Delta Lake as they arrive. It uses Structured Streaming under the hood.

---

## 1. The Problem It Solves

Without Auto Loader, you'd use a batch `spark.read` in a scheduled job:
- Every run scans **all** files to find new ones → expensive at scale
- No built-in mechanism to track what's already processed

Auto Loader uses **file notifications or directory listing** to track only new, unprocessed files — efficiently and reliably.

---

## 2. Basic Syntax

```python
df = (spark.readStream
    .format("cloudFiles")                          # ← Auto Loader format
    .option("cloudFiles.format", "json")           # source file format
    .option("cloudFiles.schemaLocation", "/checkpoint/schema")  # schema inference store
    .load("abfss://raw@storage.dfs.core.windows.net/events/"))

df.writeStream
    .format("delta")
    .option("checkpointLocation", "/checkpoint/orders")
    .trigger(availableNow=True)                    # or processingTime / continuous
    .toTable("bronze.events")
```

> [!tip] `cloudFiles.schemaLocation` is required when using schema inference. Auto Loader saves the inferred schema here so it can evolve safely over time.

---

## 3. File Discovery Modes

| Mode | How It Works | When to Use |
|:---|:---|:---|
| **Directory Listing** (default) | Lists the directory each trigger, compares to known files | Works everywhere, no extra setup |
| **File Notification** | Cloud storage sends events (SNS, Event Grid) to an SQS/Event Hub queue | Large directories with millions of files (listing becomes slow) |

```python
# Switch to file notification mode
.option("cloudFiles.useNotifications", "true")
```

---

## 4. Schema Inference & Evolution

Auto Loader can infer the schema automatically on first run and evolve it as new columns appear.

```python
# Enable schema evolution (new columns are merged, never rejected)
.option("cloudFiles.inferColumnTypes", "true")
.option("cloudFiles.schemaEvolutionMode", "addNewColumns")  # default
```

Schema evolution modes:
| Mode | Behaviour |
|:---|:---|
| `addNewColumns` | New columns added to schema automatically |
| `rescue` | Unknown columns saved to `_rescued_data` column instead |
| `failOnNewColumns` | Pipeline fails if schema changes |
| `none` | No evolution — new columns ignored |

> [!note] The `_rescued_data` column
> When a column doesn't match the schema, its data is saved as JSON in `_rescued_data` rather than being lost. Useful for debugging schema mismatches.

---

## 5. Trigger Modes

```python
# Process all available files now, then stop (batch-style)
.trigger(availableNow=True)

# Run every 30 seconds
.trigger(processingTime="30 seconds")

# Continuous processing (low latency, ~1ms)
.trigger(continuous="1 second")
```

> [!tip] `availableNow=True` is like a "smart batch" — it processes everything waiting, then terminates. Ideal for scheduled jobs.

---

## 6. Checkpointing

```python
.option("checkpointLocation", "/path/to/checkpoint")
```

The checkpoint directory stores:
- Which files have been processed (so they're never reprocessed)
- Stream state for recovery

> [!warning] Exam trap
> **Never share checkpoint locations between streams.** Each Auto Loader stream needs its own unique checkpoint directory.

---

## 7. Auto Loader vs. COPY INTO

| Feature | Auto Loader | COPY INTO |
|:---|:---|:---|
| **Type** | Streaming (incremental) | SQL command (batch) |
| **Scale** | Millions of files | Thousands of files |
| **Schema evolution** | Yes | Limited |
| **Best for** | Continuous, always-on ingestion | One-time or occasional loads |

```sql
-- COPY INTO syntax (alternative to Auto Loader for smaller loads)
COPY INTO bronze.events
FROM 'abfss://raw@storage.dfs.core.windows.net/events/'
FILEFORMAT = JSON
FILES = ('file1.json', 'file2.json');  -- or PATTERN for wildcards
```

---

> Related: [[db-delta]] (target Delta tables), [[db-streaming]] (Structured Streaming concepts), [[db-dlt]] (Auto Loader inside DLT pipelines)

---

## 8. Why Exactly-Once Matters (Conceptual Depth)

**Why file listing is slow at scale:** A data lake receiving 1,000 new files per hour means 24,000 files/day, 168,000/week. Listing all files every run and comparing to a processed-files list becomes very slow. File Notification mode uses cloud-native event queues (AWS SQS, Azure Event Hub) to receive a push notification when a file lands — no listing required, O(1) per new file regardless of total directory size.

**Exactly-once semantics:** Auto Loader guarantees each file is processed exactly once as long as the checkpoint is intact. If the stream restarts after a failure, it reads the checkpoint to find the last successfully processed files and resumes from there — no duplicate processing, no missed files.

---

## 9. Auto Loader: Standalone vs. Inside DLT

When you use Auto Loader inside a DLT pipeline, DLT manages the checkpoint automatically.

| Context | Who manages checkpoint? | Need `checkpointLocation`? |
|:---|:---|:---|
| **Standalone streaming** | You | Yes — must specify it |
| **Inside DLT** | DLT manages it automatically | No — DLT creates it |

```python
# Inside DLT — no checkpointLocation needed
@dlt.table(name="bronze_events")
def bronze_events():
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/schema/events")
            .load("abfss://raw@storage.dfs.core.windows.net/events/")
    )
```

---

## 10. Practice Questions

**Q1.** Two Auto Loader streams read from the same source folder into different target tables. They share the same checkpoint location. What happens?
> **Answer:** Data corruption — streams must NEVER share checkpoint locations. Sharing causes one stream's progress to overwrite the other's, leading to files being skipped or double-processed. Always use a unique checkpoint per stream.

**Q2.** What is `availableNow=True` and how does it differ from `once=True`?
> **Answer:** Both process available data and stop. `availableNow=True` is the modern replacement for the deprecated `once=True`. Key difference: `availableNow=True` can process multiple micro-batches in parallel, while `once=True` processed everything in a single micro-batch. Use `availableNow=True`.

**Q3.** Auto Loader ingests JSON files. A new file arrives with column `discount_pct` not present before. `schemaEvolutionMode = 'addNewColumns'`. What happens?
> **Answer:** The column is automatically added to the inferred schema (stored in `schemaLocation`). The stream continues processing. Existing rows will have `null` for `discount_pct`.

**Q4.** When would you choose File Notification mode over Directory Listing mode?
> **Answer:** When the source directory contains millions of files. Directory listing scans the whole directory each trigger — with millions of files this becomes very slow. File Notification mode uses cloud event queues, receiving a push notification per new file.

**Q5.** What is the `_rescued_data` column and when does data end up there?
> **Answer:** When `schemaEvolutionMode = 'rescue'`, any column that doesn't match the current schema is serialized as JSON and saved to `_rescued_data` instead of being dropped. Useful for debugging schema mismatches without losing data.

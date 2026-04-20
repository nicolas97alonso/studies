---
tags: [databricks, streaming, structured-streaming, spark]
aliases: [Structured Streaming, Spark Streaming, readStream, writeStream]
---

# Structured Streaming

> [!important] Exam Priority: MEDIUM-HIGH
> Understand the core model (unbounded table), triggers, output modes, and checkpointing. DLT hides most of this, but the exam still tests the underlying concepts.

Structured Streaming treats a live data stream as an **unbounded table** — data is continuously appended, and you write queries against it just like a static DataFrame. Spark handles the incremental execution.

---

## 1. The Mental Model

```
Input stream → [append-only unbounded table]
                        ↓
               Your transformation query
                        ↓
              Output sink (Delta, Kafka, etc.)
```

You write a normal DataFrame query. Spark runs it incrementally as new data arrives.

---

## 2. Reading a Stream

```python
# From Delta table
df = spark.readStream.format("delta").table("bronze.events")

# From Kafka
df = (spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "host:9092")
    .option("subscribe", "my-topic")
    .load())

# From files (Auto Loader is preferred — see [[db-autoloader]])
df = spark.readStream.format("json").load("/path/to/folder/")
```

---

## 3. Writing a Stream

```python
query = (df.writeStream
    .format("delta")
    .outputMode("append")                         # see Output Modes below
    .option("checkpointLocation", "/checkpoint/") # REQUIRED
    .trigger(processingTime="10 seconds")
    .toTable("silver.events"))

# Wait for termination
query.awaitTermination()

# Monitor
query.status
query.lastProgress
```

---

## 4. Output Modes

> [!important] Exam trap
> Not all output modes work with all query types.

| Mode | What it writes | Constraint |
|:---|:---|:---|
| **Append** | Only newly added rows | Only for queries with no aggregation (or windowed aggregation with watermarks) |
| **Complete** | Entire result table from scratch | Requires aggregation — rewrites the whole output each trigger |
| **Update** | Only rows that changed since last trigger | Requires aggregation — like a diff |

---

## 5. Triggers

```python
.trigger(processingTime="30 seconds")  # micro-batch every 30s
.trigger(once=True)                    # process once then stop (DEPRECATED — use availableNow)
.trigger(availableNow=True)            # process all available data then stop
.trigger(continuous="1 second")        # experimental low-latency mode
```

---

## 6. Checkpointing

Checkpoints make streams **fault-tolerant and exactly-once**:
- Track which offsets/files have been processed
- Store aggregation state (for stateful queries)

```python
.option("checkpointLocation", "/dbfs/checkpoints/my-stream/")
```

> [!warning] Never delete the checkpoint unless you want to reprocess from scratch. Never share a checkpoint between two different streams.

---

## 7. Watermarks (Handling Late Data)

For event-time aggregations, watermarks tell Spark how long to wait for late-arriving data before closing a window.

```python
from pyspark.sql.functions import window

df_with_watermark = (df
    .withWatermark("event_time", "10 minutes")   # wait up to 10 min for late data
    .groupBy(window("event_time", "5 minutes"))   # 5-minute tumbling window
    .count())
```

---

## 8. Stateful vs. Stateless Operations

| Type | Examples | Notes |
|:---|:---|:---|
| **Stateless** | `filter`, `select`, `map` | No memory of previous batches — very fast |
| **Stateful** | `groupBy`, `join`, `window` | Spark maintains state in memory/checkpoint — requires watermarks for cleanup |

---

## 9. foreachBatch

Write to a non-native sink or perform custom logic on each micro-batch:

```python
def process_batch(batch_df, batch_id):
    # Write to multiple targets
    batch_df.write.format("delta").mode("append").saveAsTable("target_table")
    batch_df.write.format("parquet").save("/archive/")

(df.writeStream
    .foreachBatch(process_batch)
    .option("checkpointLocation", "/checkpoint/")
    .start())
```

---

> Related: [[db-autoloader]] (file-based streaming ingestion), [[db-dlt]] (declarative streaming pipelines), [[db-delta]] (Delta as a streaming sink/source)

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

---

## 10. Stream-Static vs. Stream-Stream Joins

### Stream-Static Join (Common Pattern)
Join a streaming DataFrame with a static lookup table. The static side is loaded once and broadcast.

```python
# Static lookup table
customers_static = spark.read.table("silver.customers")

# Streaming events
events_stream = spark.readStream.format("delta").table("bronze.events")

# Join — stream-static, no watermark needed
enriched = events_stream.join(customers_static, "customer_id")

enriched.writeStream.format("delta").option("checkpointLocation", "...").toTable("silver.enriched_events")
```

> [!tip] Stream-static joins don't require watermarks. The static table is broadcast to executors and joined at each micro-batch.

### Stream-Stream Join
Both sides are streams. Requires watermarks to bound the state size.

```python
clicks = (spark.readStream.format("delta").table("bronze.clicks")
    .withWatermark("click_time", "10 minutes"))

impressions = (spark.readStream.format("delta").table("bronze.impressions")
    .withWatermark("impression_time", "20 minutes"))

joined = clicks.join(
    impressions,
    expr("click_ad_id = impression_ad_id AND "
         "click_time BETWEEN impression_time AND impression_time + INTERVAL 1 HOUR")
)
```

> [!warning] Stream-stream joins are stateful — Spark must buffer events waiting for a match. Always use watermarks to bound state size, otherwise memory grows unbounded.

---

## 11. Streaming vs. Batch: When to Use Each

| Scenario | Recommendation | Why |
|:---|:---|:---|
| New files land hourly, processed once an hour | **Batch or `availableNow=True`** | No need for always-on stream |
| New files land continuously, need < 5 min latency | **Auto Loader streaming** | Incremental as files arrive |
| Need < 1 min latency | **DLT Continuous or Kafka + Structured Streaming** | Sub-minute requires always-on processing |
| Aggregated daily report | **Batch job** | Full recalculation is simpler, more accurate |
| CDC feed (Kafka/Kinesis) | **Structured Streaming or DLT APPLY CHANGES** | Continuous event processing |

> [!important] Exam trap: "incremental" ≠ "streaming"
> `trigger(availableNow=True)` is **incremental but batch** — it processes new data and stops. True streaming runs continuously. Both process only new data; only streaming runs forever.

---

## 12. Practice Questions

**Q1.** A streaming query writes to Delta with `outputMode("complete")`. The query is `GROUP BY product` summing revenue. After 3 micro-batches, what is in the output table?
> **Answer:** One row per product with the **total revenue from all batches combined** — the entire result table is rewritten from scratch each trigger. `complete` mode rewrites all rows, not just new ones.

**Q2.** You have `outputMode("append")` with a `groupBy().count()` aggregation and no watermark. Will this work?
> **Answer:** No — `append` mode with aggregation requires watermarks. Without a watermark, Spark can't know when aggregation results are final. Use `complete` or `update` mode for aggregations.

**Q3.** A streaming query fails mid-run. On restart, will any data be processed twice?
> **Answer:** No — checkpointing ensures exactly-once semantics. Spark reads the checkpoint to find the last successfully committed offset and resumes from there.

**Q4.** What is a watermark and why do you need one for windowed aggregations?
> **Answer:** A watermark defines the maximum expected lateness of data. Without it, Spark must hold all window state forever waiting for late data. With a watermark, Spark can safely discard state for windows older than the watermark and emit results — essential for bounded memory usage.

**Q5.** You need to write streaming data to both a Delta table AND a REST API. Which method handles this?
> **Answer:** `foreachBatch` — it gives you each micro-batch as a static DataFrame and lets you write custom logic, including multiple sinks.

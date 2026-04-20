---
tags: [databricks, delta-lake, storage, acid, exam-priority]
aliases: [Delta Lake, Delta Table, Transaction Log]
---

# Delta Lake

> [!important] Exam Priority: HIGH
> Delta Lake is the most heavily tested topic. Expect 20–30% of questions to touch Delta Lake concepts.

Delta Lake is an open-source storage layer that adds reliability to data lakes. Sits on top of Parquet files and adds a **transaction log** to enable ACID transactions, time travel, and schema enforcement.

---

## 1. How Delta Lake Works: The Transaction Log

Every Delta table has a `_delta_log/` directory next to the data files.

```
my_table/
├── _delta_log/
│   ├── 00000000000000000000.json   ← commit 0
│   ├── 00000000000000000001.json   ← commit 1
│   ├── 00000000000000000010.json   ← commit 10
│   └── 00000000000000000010.checkpoint.parquet  ← checkpoint every 10 commits
├── part-00000-xxxx.parquet
└── part-00001-xxxx.parquet
```

Each JSON commit records:
- **Add**: new files written
- **Remove** (tombstone): old files logically deleted (still exist on disk)
- Schema, metadata, statistics for data skipping

> [!tip] Checkpoint files
> Every 10 commits, Delta writes a `.checkpoint.parquet` to avoid replaying thousands of JSON files. Reading the latest checkpoint + any JSON files after it gives you the current table state.

---

## 2. ACID Transactions

| Property | What it means in Delta |
|:---|:---|
| **Atomicity** | Either all files in a write are committed or none are |
| **Consistency** | Schema enforcement ensures data is always valid |
| **Isolation** | Concurrent readers/writers don't interfere (optimistic concurrency) |
| **Durability** | Once committed to the log, changes survive failures |

> [!note] Exam trap
> Plain Parquet files have **no** ACID guarantees. If a write fails halfway, you get partial data. Delta prevents this.

---

## 3. Creating Delta Tables

```sql
-- From scratch (default format in Databricks is Delta)
CREATE TABLE orders (
  id     BIGINT,
  amount DOUBLE,
  status STRING,
  date   DATE
) USING DELTA;

-- From an existing file
CREATE TABLE orders
USING DELTA
LOCATION 'abfss://raw@storage.dfs.core.windows.net/orders/';

-- CTAS (Create Table As Select)
CREATE TABLE orders_backup AS
SELECT * FROM orders WHERE date >= '2024-01-01';

-- Convert existing Parquet to Delta
CONVERT TO DELTA parquet.`/path/to/parquet/`;
```

---

## 4. DML Operations

Delta supports full SQL DML — unlike plain Parquet which is read-only.

```sql
-- Insert
INSERT INTO orders VALUES (1, 99.99, 'open', '2024-01-15');
INSERT INTO orders SELECT * FROM staging_orders;

-- Update
UPDATE orders SET status = 'closed' WHERE id = 1;

-- Delete
DELETE FROM orders WHERE status = 'cancelled';
```

### MERGE INTO (Upsert)

> [!important] Exam Priority: HIGH
> MERGE is a very common exam question. Know the syntax and clause options.

```sql
MERGE INTO target t
USING source s
ON t.id = s.id
WHEN MATCHED AND s.status = 'deleted' THEN DELETE
WHEN MATCHED THEN UPDATE SET
  t.amount = s.amount,
  t.status = s.status
WHEN NOT MATCHED THEN INSERT (id, amount, status, date)
  VALUES (s.id, s.amount, s.status, s.date)
WHEN NOT MATCHED BY SOURCE THEN DELETE;  -- rows in target with no match in source
```

Clauses available: `WHEN MATCHED`, `WHEN NOT MATCHED`, `WHEN NOT MATCHED BY SOURCE`

---

## 5. Time Travel

Delta preserves previous versions of the table. You can query any version.

```sql
-- By version number
SELECT * FROM orders VERSION AS OF 5;

-- By timestamp
SELECT * FROM orders TIMESTAMP AS OF '2024-06-01T12:00:00';

-- In PySpark
df = spark.read.format("delta").option("versionAsOf", 5).load("/path/to/table")
df = spark.read.format("delta").option("timestampAsOf", "2024-06-01").load("/path/to/table")

-- Restore a table to a prior version
RESTORE TABLE orders TO VERSION AS OF 5;
RESTORE TABLE orders TO TIMESTAMP AS OF '2024-06-01';
```

```sql
-- View full history
DESCRIBE HISTORY orders;
```

> [!warning] VACUUM kills time travel
> Once you run VACUUM, you CANNOT time travel before the retention cutoff. Default retention = 7 days (168 hours).

---

## 6. Schema Management

### Schema Enforcement (default ON)
Delta rejects writes where the data doesn't match the table schema.
- Extra columns in the source → **error**
- Wrong data types → **error**

### Schema Evolution (opt-in)
Allow the schema to grow when new columns arrive.

```python
# PySpark
df.write.format("delta").option("mergeSchema", "true").mode("append").save(path)

# Or set globally
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
```

```sql
-- SQL equivalent
ALTER TABLE orders ADD COLUMNS (discount DOUBLE);
```

> [!tip] Exam tip
> Schema **enforcement** = Delta rejects bad data (default, protects data quality).
> Schema **evolution** = Delta accepts new columns (opt-in, controlled growth).

---

## 7. Performance: OPTIMIZE, Z-ORDER, VACUUM

### OPTIMIZE
Compacts small files into larger files (~1 GB each). Small files are a common cause of slow reads.

```sql
OPTIMIZE orders;
```

### Z-ORDER
Co-locates related data in the same files. Dramatically speeds up queries that filter on the Z-ORDER columns. Must be combined with OPTIMIZE.

```sql
OPTIMIZE orders ZORDER BY (country, customer_id);
```

> [!note] Z-ORDER vs partitioning
> Partitioning physically separates data into folders. Z-ORDER clusters data within files. Use partitioning for very high-cardinality splits (e.g., by year/month), Z-ORDER for columns you filter on frequently.

### VACUUM
Permanently deletes data files no longer referenced by the transaction log.

```sql
VACUUM orders;                        -- uses default retention (7 days / 168 hours)
VACUUM orders RETAIN 240 HOURS;       -- custom retention
VACUUM orders RETAIN 0 HOURS DRY RUN; -- preview what would be deleted
```

> [!warning] Exam trap
> You must set `spark.databricks.delta.retentionDurationCheck.enabled = false` to VACUUM below 7 days. Databricks blocks sub-7-day vacuums by default to protect time travel.

---

## 8. Change Data Feed (CDF)

Tracks row-level changes (inserts, updates, deletes) so downstream consumers can process incremental changes efficiently.

```sql
-- Enable on existing table
ALTER TABLE orders SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');

-- Enable at creation
CREATE TABLE orders (...) TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');
```

```python
# Read changes
changes = (spark.readStream
    .format("delta")
    .option("readChangeFeed", "true")
    .option("startingVersion", 0)
    .table("orders"))
```

Change types in the `_change_type` column:
| Value | Meaning |
|:---|:---|
| `insert` | New row added |
| `update_preimage` | Old value before update |
| `update_postimage` | New value after update |
| `delete` | Row deleted |

---

## 9. Table Details & Properties

```sql
-- Inspect Delta table metadata
DESCRIBE DETAIL orders;      -- file count, size, location, format
DESCRIBE HISTORY orders;     -- all commits, operations, who ran them
DESCRIBE TABLE orders;       -- column names, types, comments

-- Set/get table properties
ALTER TABLE orders SET TBLPROPERTIES ('delta.logRetentionDuration' = 'interval 30 days');
SHOW TBLPROPERTIES orders;
```

---

## 10. CLONE

```sql
-- Shallow clone: copies metadata only, references same data files
CREATE TABLE orders_clone SHALLOW CLONE orders;

-- Deep clone: copies metadata AND data files
CREATE TABLE orders_backup DEEP CLONE orders;
```

> [!tip] Use DEEP CLONE for backups, SHALLOW CLONE for fast dev/test environments.

---

> Related: [[db-autoloader]] (streaming into Delta), [[db-dlt]] (Delta Live Tables pipelines), [[db-sparksql]] (SQL operations), [[db-streaming]] (Structured Streaming with Delta)

---

## 11. Data Skipping

Delta automatically collects **min/max statistics** for each data file (up to 32 columns by default). When a query filters on a column, Delta reads these stats and skips files that can't contain matching rows — without opening them.

**Example:** `WHERE date = '2024-06-15'`
- Delta checks the `date` min/max for each file
- Skips any file where `max_date < '2024-06-15'` or `min_date > '2024-06-15'`
- Only reads files that _could_ contain the date

> [!tip] Why Z-ORDER helps data skipping
> Z-ORDER clusters rows with similar values into the same files. This narrows the min/max range per file, making data skipping dramatically more effective. Without Z-ORDER, min/max ranges overlap heavily across files.

```sql
-- See statistics collected
DESCRIBE DETAIL orders;   -- shows numFiles, statistics columns
```

> [!note] Column limit
> By default, Delta collects stats on the first 32 columns only. Move your filter columns to the front of the schema if you have many columns.

---

## 12. Liquid Clustering (Modern Alternative to Z-ORDER)

**Problem with Z-ORDER + OPTIMIZE:** Full table rewrites are needed to maintain clustering. Expensive on large tables.

**Liquid Clustering** is the modern solution: clustering is applied **incrementally** — only new/changed files are re-clustered, not the whole table.

```sql
-- Enable at table creation
CREATE TABLE orders (
  id     BIGINT,
  date   DATE,
  region STRING
) USING DELTA
CLUSTER BY (date, region);

-- Enable on existing table
ALTER TABLE orders CLUSTER BY (date, region);

-- Then run OPTIMIZE as usual — Delta handles the rest
OPTIMIZE orders;
```

| Feature | Z-ORDER | Liquid Clustering |
|:---|:---|:---|
| How it clusters | Full table rewrite | Incremental — only changed data |
| Partition dependency | Can combine with partitioning | No partitioning needed |
| Performance | Good | Better for large, frequently-updated tables |
| Availability | GA | GA in DBR 13.3+ |

> [!tip] Exam tip
> Liquid Clustering is the **recommended approach** for new tables. Z-ORDER is still valid but requires more maintenance. If the exam asks about clustering for frequently-updated tables, Liquid Clustering is the better answer.

---

## 13. Generated Columns

Columns whose value is automatically computed from other columns. Databricks stores them physically (like regular columns) and keeps them in sync on write.

```sql
CREATE TABLE events (
  ts        TIMESTAMP,
  date      DATE GENERATED ALWAYS AS (CAST(ts AS DATE)),
  year      INT  GENERATED ALWAYS AS (YEAR(ts))
) USING DELTA
PARTITIONED BY (date);  -- partition on the generated column!
```

> [!tip] Exam use case
> Use generated columns to **auto-partition on a derived date** from a timestamp column. When you filter `WHERE ts BETWEEN ...`, Delta can use partition pruning on `date` automatically.

---

## 14. How Reads Work: The Full Picture

To read a Delta table, Spark:
1. Finds the latest `.checkpoint.parquet` in `_delta_log/`
2. Replays any JSON commit files written after the checkpoint
3. Reconstructs the current list of **live Parquet files** (adds minus removes)
4. Reads only those files — applying data skipping using per-file statistics

This is why Delta reads are **consistent and reliable** — you always get a complete, committed snapshot regardless of concurrent writers.

**Optimistic Concurrency:** Multiple writers can write simultaneously. Each reads the current version, performs their write, then tries to commit. If the log version changed while they were writing, Delta checks for conflicts. If the changes don't overlap (different rows/partitions), both succeed. If they conflict, one is retried or fails with a `ConcurrentModificationException`.

---

## 15. Practice Questions

**Q1.** You run `VACUUM orders RETAIN 0 HOURS`. A user then tries `SELECT * FROM orders VERSION AS OF 5`. What happens?
> **Answer:** Error — VACUUM deleted the data files for old versions. Time travel below the retention cutoff is no longer possible. You must set `spark.databricks.delta.retentionDurationCheck.enabled = false` to run VACUUM below 7 days.

**Q2.** A write fails halfway through updating 10,000 rows. What is the state of the Delta table?
> **Answer:** The table is unchanged — atomicity guarantees the partial write is never committed to the transaction log. Readers see the last complete version.

**Q3.** What is the difference between `WHEN NOT MATCHED` and `WHEN NOT MATCHED BY SOURCE` in MERGE?
> **Answer:** `WHEN NOT MATCHED` — rows in the **source** that have no match in the target (inserts). `WHEN NOT MATCHED BY SOURCE` — rows in the **target** that have no match in the source (useful for soft-deletes or keeping the target in sync with the source).

**Q4.** You enable Change Data Feed on a table. A row is updated. What `_change_type` values appear?
> **Answer:** Two rows: `update_preimage` (old values before the update) and `update_postimage` (new values after the update).

**Q5.** What happens when you `SHALLOW CLONE` a Delta table and modify the clone?
> **Answer:** The clone gets its own transaction log. Changes to the clone do NOT affect the source. New data files are written for the clone. The clone still references the original data files for existing data (no copy made).

**Q6.** What does Z-ORDER actually do physically, and why does it help query performance?
> **Answer:** Z-ORDER rewrites data files so that rows with similar values for the Z-ORDER columns are stored together in the same files. This tightens the min/max statistics per file, allowing Delta's data skipping to eliminate more files when filtering on those columns.

**Q7.** You set `spark.databricks.delta.schema.autoMerge.enabled = true`. A new column arrives in source data. What happens on the next write?
> **Answer:** The new column is automatically added to the Delta table schema and data is written including the new column. Existing rows will have `null` for the new column.

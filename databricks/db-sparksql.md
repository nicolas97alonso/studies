---
tags: [databricks, sparksql, tables, unity-catalog, hive, exam-priority]
aliases: [Spark SQL, Unity Catalog Tables, Hive Metastore, SQL DDL]
---

# Spark SQL & the Table Model

> [!important] Exam Priority: HIGH
> Know the difference between managed vs external tables, view types, and DESCRIBE commands. Heavily tested.

---

## 1. Metastore Basics

Data files in a Data Lake (Parquet, Delta, CSV) are just files. Spark SQL needs a **metastore** to understand them as tables — mapping table names to file locations, schemas, and partition info.

| Metastore | Namespace | Status |
|:---|:---|:---|
| **Hive Metastore** | `schema.table` (2 levels) | Legacy — still used in older workspaces |
| **Unity Catalog** | `catalog.schema.table` (3 levels) | Current standard — see [[db-unity-catalog]] |

> [!note] The `hive_metastore` catalog
> In Unity Catalog workspaces, the legacy Hive Metastore is accessible as `hive_metastore.schema.table`. This allows gradual migration.

---

## 2. Table Types

### Managed Tables
Spark manages **both** metadata and data files.
- Data is stored in the catalog's default location (controlled by UC or Hive Metastore)
- **`DROP TABLE` deletes metadata AND data files**

```sql
CREATE TABLE orders (
    id     BIGINT,
    amount DOUBLE,
    status STRING,
    date   DATE
) USING DELTA;
```

### External Tables
Spark manages only metadata. You control the file location.
- **`DROP TABLE` removes metadata only — data files are preserved**

```sql
CREATE TABLE orders_external
USING DELTA
LOCATION 'abfss://raw@storage.dfs.core.windows.net/orders/';
```

> [!important] Exam trap
> The key difference: **DROP TABLE on a managed table = data is gone**. DROP TABLE on an external table = only metadata is removed, files remain.

---

## 3. Views

| Type | Scope | When dropped |
|:---|:---|:---|
| **View** | Workspace-persistent | Only when you DROP it |
| **Temp View** | Session-scoped (current SparkSession) | When SparkSession ends or cluster restarts |
| **Global Temp View** | Cluster-scoped (all notebooks on same cluster) | When cluster restarts |

```sql
-- Permanent view
CREATE VIEW high_value_orders AS
SELECT * FROM orders WHERE amount > 1000;

-- Temp view
CREATE OR REPLACE TEMP VIEW recent_orders AS
SELECT * FROM orders WHERE date >= '2024-01-01';

-- Global temp view (requires global_temp schema prefix)
CREATE OR REPLACE GLOBAL TEMP VIEW all_orders AS
SELECT * FROM orders;

SELECT * FROM global_temp.all_orders;
```

---

## 4. DESCRIBE Commands (Exam Frequently Tested)

```sql
-- Column names, types, comments
DESCRIBE TABLE orders;
DESCRIBE orders;            -- shorthand

-- Delta-specific: file count, size, location, format, partitions
DESCRIBE DETAIL orders;

-- Full Delta commit history
DESCRIBE HISTORY orders;

-- Show all tables in current schema
SHOW TABLES;
SHOW TABLES IN my_schema;

-- Show table DDL
SHOW CREATE TABLE orders;

-- Show table properties
SHOW TBLPROPERTIES orders;
```

---

## 5. DDL: Create, Alter, Drop

```sql
-- Create table with partitioning
CREATE TABLE events (
    id        BIGINT,
    event_type STRING,
    ts        TIMESTAMP,
    date      DATE
) USING DELTA
PARTITIONED BY (date)
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');

-- Add a column
ALTER TABLE orders ADD COLUMNS (discount DOUBLE AFTER amount);

-- Rename a column
ALTER TABLE orders RENAME COLUMN old_name TO new_name;

-- Change column type (Delta supports type widening)
ALTER TABLE orders ALTER COLUMN amount TYPE BIGINT;

-- Drop a column
ALTER TABLE orders DROP COLUMN unused_col;

-- Drop table
DROP TABLE IF EXISTS old_table;

-- Truncate (delete all rows, keep schema — managed tables only)
TRUNCATE TABLE staging_orders;
```

---

## 6. Common Delta SQL Operations

```sql
-- Optimize file sizes
OPTIMIZE orders;
OPTIMIZE orders ZORDER BY (customer_id, date);

-- Remove stale data files
VACUUM orders RETAIN 168 HOURS;

-- Time travel
SELECT * FROM orders VERSION AS OF 10;
SELECT * FROM orders TIMESTAMP AS OF '2024-06-01';

-- Restore to previous version
RESTORE TABLE orders TO VERSION AS OF 10;

-- Clone a table
CREATE TABLE orders_dev SHALLOW CLONE orders;
CREATE TABLE orders_backup DEEP CLONE orders;
```

---

## 7. Mixing SQL and PySpark

```python
# SQL → DataFrame
df = spark.sql("SELECT * FROM orders WHERE amount > 100")

# DataFrame → SQL (via temp view)
df.createOrReplaceTempView("orders_temp")
result = spark.sql("SELECT COUNT(*) FROM orders_temp GROUP BY status")

# DataFrame → permanent table
df.write.format("delta").mode("overwrite").saveAsTable("my_schema.orders")
df.write.format("delta").mode("append").saveAsTable("my_schema.orders")
```

### Write Modes

| Mode | Behaviour |
|:---|:---|
| `overwrite` | Replace the entire table |
| `append` | Add rows to existing table |
| `ignore` | No-op if table already exists |
| `error` | Fail if table already exists (default) |

---

## 8. Databases (Schemas)

```sql
CREATE DATABASE IF NOT EXISTS my_db
LOCATION 'abfss://data@storage.dfs.core.windows.net/my_db/';

USE DATABASE my_db;
SHOW DATABASES;
DROP DATABASE my_db CASCADE;  -- CASCADE drops all tables inside
```

---

> Related: [[db-delta]] (Delta operations), [[db-unity-catalog]] (UC table model and permissions), [[db-spark]] (execution engine), [[db-datalake]] (storage layer)

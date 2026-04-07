---
tags: [databricks, sparksql, tables, unitycatalog, hive]
aliases: [Spark SQL, Unity Catalog Tables, Hive Metastore]
---

# Spark SQL & the Table Model

## Hive Metastore

> [!warning] Legacy Reference
> Hive Metastore is the old metadata management layer. **Unity Catalog is the current standard** in Databricks. This section is here for understanding older environments.

### Why a Metastore?
Data files in a Data Lake (Parquet, Delta, CSV) are just files. Spark SQL needs a **metastore** to understand them as tables — mapping table names to file locations, schemas, and partition info.

The most common metastore is **Apache Hive Metastore**, which Databricks has historically used either:
- As a **Databricks-managed** internal metastore (default)
- As an **external** metastore (Azure SQL, MySQL, etc.) shared across workspaces

---

## Unity Catalog (Current Standard)

Unity Catalog replaces per-workspace Hive Metastores with a single, account-level governance layer.

### Three-Level Namespace

```
Catalog
└── Schema (Database)
    └── Table / View
```

```sql
-- Fully qualified name
SELECT * FROM my_catalog.my_schema.my_table;

-- Set defaults so you don't have to type them every time
USE CATALOG my_catalog;
USE SCHEMA my_schema;
SELECT * FROM my_table;
```

---

## Table Types

### Managed Tables
Spark manages **both** the metadata and the underlying data files.
- Data is stored in the catalog's default storage location (ADLS, managed by Unity Catalog).
- `DROP TABLE` deletes the metadata **and** the data files.

```sql
CREATE TABLE sales (
    id    INT,
    amount DOUBLE,
    date  DATE
);
```

### External Tables
Spark manages only the metadata. You control where the files live.
- You specify the file location explicitly.
- `DROP TABLE` removes the metadata only — **data files are preserved**.

```sql
CREATE TABLE sales_external
USING DELTA
LOCATION 'abfss://raw@mystorageaccount.dfs.core.windows.net/sales/';
```

> Use External Tables when you need to share data with systems outside Databricks or need explicit control over file lifecycle.

---

## Views

| Type | Description |
| :--- | :--- |
| **View** | Saved SQL query, no data stored. Runs the query on access. |
| **Temporary View** | Session-scoped — disappears when the SparkSession ends. Not visible to other users. |
| **Global Temp View** | Cluster-scoped — shared across notebooks on the same cluster. Dropped when the cluster restarts. |

```sql
-- Permanent view
CREATE VIEW high_value_orders AS
SELECT * FROM orders WHERE amount > 1000;

-- Temp view (session only)
CREATE OR REPLACE TEMP VIEW recent_orders AS
SELECT * FROM orders WHERE date >= '2024-01-01';

-- Global temp view
CREATE OR REPLACE GLOBAL TEMP VIEW all_orders AS
SELECT * FROM orders;

-- Query global temp view (requires global_temp prefix)
SELECT * FROM global_temp.all_orders;
```

---

## Common Spark SQL Operations

```sql
-- Show available databases/schemas
SHOW DATABASES;
SHOW SCHEMAS IN my_catalog;

-- Inspect a table
DESCRIBE TABLE my_table;
DESCRIBE DETAIL my_table;   -- Delta-specific: file stats, history

-- See table history (Delta only)
DESCRIBE HISTORY my_table;

-- Optimize a Delta table
OPTIMIZE my_table;
VACUUM my_table RETAIN 168 HOURS;
```

---

## Mixing SQL and PySpark

You can move between SQL and DataFrames freely:

```python
# SQL → DataFrame
df = spark.sql("SELECT * FROM my_table WHERE amount > 100")

# DataFrame → Temp View → SQL
df.createOrReplaceTempView("my_temp_table")
result = spark.sql("SELECT COUNT(*) FROM my_temp_table")
```

---

> Related: [[db-spark]] (Spark execution model), [[db-datalake]] (where the files live), [[db-databricks]] (cluster setup for running SQL)

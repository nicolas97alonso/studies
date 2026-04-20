---
tags: [databricks, unity-catalog, governance, security, exam-priority]
aliases: [Unity Catalog, UC, Data Governance, Metastore]
---

# Unity Catalog

> [!important] Exam Priority: HIGH
> Unity Catalog is the modern governance layer. The exam tests the 3-level namespace, object types, and privilege model.

Unity Catalog (UC) is a unified data governance solution for Databricks. It provides centralized access control, auditing, lineage, and data discovery across all Databricks workspaces in an account.

---

## 1. The Three-Level Namespace

```
Account
└── Metastore (1 per region, shared across workspaces)
    └── Catalog
        └── Schema (Database)
            └── Table / View / Volume / Function
```

```sql
-- Fully qualified reference
SELECT * FROM my_catalog.my_schema.my_table;

-- Set defaults
USE CATALOG my_catalog;
USE SCHEMA my_schema;
SELECT * FROM my_table;  -- works after setting defaults
```

> [!note] Exam trap: Hive Metastore vs Unity Catalog
> The legacy **Hive Metastore** uses a 2-level namespace: `schema.table`.
> Unity Catalog uses **3 levels**: `catalog.schema.table`.
> The `hive_metastore` catalog is a special catalog that exposes the legacy Hive Metastore in UC.

---

## 2. Securable Objects

| Object | Level | Description |
|:---|:---|:---|
| **Metastore** | Account | Top-level container, 1 per region |
| **Catalog** | Metastore | Groups schemas together |
| **Schema** | Catalog | Groups tables/views/functions |
| **Table** | Schema | Managed or external Delta/Parquet/etc. |
| **View** | Schema | Saved SQL query over tables |
| **Volume** | Schema | Non-tabular file storage (replaces DBFS mounts) |
| **External Location** | Metastore | Cloud storage path + storage credential |
| **Storage Credential** | Metastore | Cloud IAM credential for accessing storage |
| **Share** | Metastore | Delta Sharing object for cross-org data sharing |

---

## 3. Privilege Model

Privileges follow the object hierarchy — granting on a catalog covers all schemas/tables within it.

### Core Privileges

| Privilege | Applies To | What It Allows |
|:---|:---|:---|
| `USE CATALOG` | Catalog | Required to access anything inside |
| `USE SCHEMA` | Schema | Required to access tables/views in the schema |
| `SELECT` | Table/View | Read data |
| `MODIFY` | Table | Insert/update/delete rows |
| `CREATE TABLE` | Schema | Create new tables |
| `CREATE SCHEMA` | Catalog | Create new schemas |
| `ALL PRIVILEGES` | Any | All privileges on that object |

```sql
-- Grant read access to a user
GRANT USE CATALOG ON CATALOG main TO `analyst@company.com`;
GRANT USE SCHEMA ON SCHEMA main.sales TO `analyst@company.com`;
GRANT SELECT ON TABLE main.sales.orders TO `analyst@company.com`;

-- Grant to a group (preferred over individual users)
GRANT SELECT ON TABLE main.sales.orders TO `data_analysts`;

-- Revoke
REVOKE SELECT ON TABLE main.sales.orders FROM `analyst@company.com`;

-- Show grants
SHOW GRANTS ON TABLE main.sales.orders;
```

> [!tip] Best practice: manage access via **groups** (defined in the account identity provider), not individual users. Changing group membership is much easier than updating individual grants.

---

## 4. Table Types in Unity Catalog

### Managed Tables
- Data stored in the catalog's default storage (managed by UC)
- `DROP TABLE` deletes both metadata and data files

### External Tables
- Data stored in a location you control (requires External Location + Storage Credential)
- `DROP TABLE` removes metadata only — files are preserved

```sql
-- Create external table in UC
CREATE TABLE main.sales.orders_ext
USING DELTA
LOCATION 'abfss://data@storage.dfs.core.windows.net/orders/';
```

### Volumes
Volumes are UC-managed paths for non-tabular files (CSVs, images, models, etc.) — the modern replacement for DBFS mounts.

```sql
-- Create a volume
CREATE VOLUME main.raw.landing;

-- Write to it
COPY INTO main.bronze.events FROM '/Volumes/main/raw/landing/events/';

-- Path format
/Volumes/<catalog>/<schema>/<volume>/<path>
```

---

## 5. Data Lineage

UC automatically tracks column-level lineage. In the UI: **Catalog Explorer → Table → Lineage tab**.

No setup required — Databricks tracks all reads/writes through SQL, PySpark, and DLT automatically.

---

## 6. Audit Logs

All access events (who queried what, when) are captured in UC audit logs. Exposed via:

```sql
SELECT * FROM system.access.audit
WHERE event_type = 'databricksAccess'
LIMIT 100;
```

---

## 7. Delta Sharing (Cross-Organization)

Share live Delta tables with external organizations without copying data:

```sql
-- Create a share
CREATE SHARE my_share;
ALTER SHARE my_share ADD TABLE main.sales.orders;

-- Create a recipient (external org)
CREATE RECIPIENT acme_corp;

-- Grant share to recipient
GRANT SELECT ON SHARE my_share TO RECIPIENT acme_corp;
```

The recipient reads the data using their own Databricks (or open-source Delta Sharing client) — no data is copied.

---

> Related: [[db-sparksql]] (SQL operations on UC tables), [[db-datalake]] (storage credentials for external tables), [[db-databricks]] (cluster access modes for UC)

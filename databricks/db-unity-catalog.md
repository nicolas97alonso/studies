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

---

## 8. Row-Level & Column-Level Security (Dynamic Views)

> [!important] Exam Priority: HIGH
> Use **dynamic views** to enforce row and column-level security based on who's querying. The pattern: grant access to the VIEW, not the underlying table.

### Row-Level Security

```sql
-- Dynamic view that filters rows based on group membership
CREATE VIEW main.sales.orders_secure AS
SELECT * FROM main.sales.orders
WHERE
  (is_account_group_member('region_emea') AND region = 'EMEA')
  OR (is_account_group_member('region_apac') AND region = 'APAC')
  OR is_account_group_member('data_admins');  -- admins see all

-- Grant access to the VIEW, revoke direct table access
REVOKE SELECT ON TABLE main.sales.orders FROM `analysts`;
GRANT SELECT ON VIEW main.sales.orders_secure TO `analysts`;
```

### Column-Level Security (Masking)

```sql
CREATE VIEW main.sales.customers_masked AS
SELECT
  customer_id,
  name,
  CASE
    WHEN is_account_group_member('pii_allowed') THEN email
    ELSE '***MASKED***'
  END AS email
FROM main.sales.customers;
```

> [!note] `current_user()` vs `is_account_group_member()`
> `current_user()` returns the calling user's email. `is_account_group_member('group')` returns true/false. Use groups to manage access by team/role rather than individual user.

---

## 9. External Locations & Storage Credentials

External Tables in UC require a two-step setup before creating any tables:

```
Storage Credential  →  External Location  →  External Table / Volume
(IAM / Service Principal)  (storage path)       (metadata)
```

```sql
-- Step 1: Create a Storage Credential (cloud IAM role)
CREATE STORAGE CREDENTIAL my_adls_cred
WITH AZURE_MANAGED_IDENTITY (DIRECTORY_ID='...', APPLICATION_ID='...');

-- Step 2: Create an External Location (map credential to a path)
CREATE EXTERNAL LOCATION my_data_location
URL 'abfss://data@mystorageaccount.dfs.core.windows.net/'
WITH (STORAGE CREDENTIAL my_adls_cred);

-- Step 3: Create External Table (just needs the location path)
CREATE TABLE main.bronze.raw_events
USING DELTA
LOCATION 'abfss://data@mystorageaccount.dfs.core.windows.net/events/';
```

> [!tip] Set up Storage Credentials and External Locations once per storage path. All tables pointing to that path reuse the same credential — no per-table credential management.

---

## 10. Practice Questions

**Q1.** A table `main.sales.orders` is a managed table. A user runs `DROP TABLE main.sales.orders`. What is deleted?
> **Answer:** Both metadata AND the underlying data files. For an **external table**, only metadata is removed — files are preserved.

**Q2.** What three privileges must a user have to run `SELECT * FROM main.sales.orders`?
> **Answer:** `USE CATALOG` on catalog `main`, `USE SCHEMA` on schema `main.sales`, AND `SELECT` on table `main.sales.orders`. Missing any one causes access denied.

**Q3.** What cluster access mode is required to use Unity Catalog row-level security via dynamic views?
> **Answer:** **Single User** or **Shared**. No Isolation Shared does NOT support fine-grained UC access controls.

**Q4.** What is the difference between a Volume and an External Table in Unity Catalog?
> **Answer:** A Volume is for **non-tabular files** (CSVs, images, model artifacts) — it's a managed path, not a queryable table. An External Table points to structured data that Spark can query as a table.

**Q5.** A company has 3 Databricks workspaces in the same region. How many UC Metastores do they need?
> **Answer:** One metastore per region. All 3 workspaces share a single metastore — data and governance policies are unified across workspaces.

**Q6.** You grant `SELECT ON TABLE orders TO data_analysts`. Then you add the user to `senior_analysts` and grant `SELECT ON ALL TABLES IN SCHEMA main.sales TO senior_analysts`. Does the user have SELECT on `orders`?
> **Answer:** Yes — UC uses additive permissions. The user gets the union of all privileges from all groups they belong to.

---
tags: [databricks, dbfs, storage, legacy]
aliases: [DBFS, Databricks File System]
---

# Databricks File System (DBFS)

> [!warning] Legacy Feature
> DBFS mounts are **not recommended for new workspaces**. Unity Catalog handles storage access in modern Databricks. This note exists as a reference for older environments.

---

## What is DBFS?

DBFS is a **distributed virtual file system** mounted on your Databricks workspace. It is an abstraction layer — the actual data lives in Azure Data Lake (or S3/GCS), but DBFS presents it as if it were a local filesystem.

---

## DBFS Root

The default storage location for a Databricks workspace.
- Backed by blob/object storage in the cloud provider's account.
- Accessible via the Databricks UI file browser.
- Saved query results and certain workspace assets are stored here.
- **Default storage for Managed Tables** (when not using Unity Catalog).

> **Do not store important data in DBFS root.** If the workspace is deleted, the DBFS root and all its data are lost.  
> **Best practice:** Create your own Azure Data Lake Gen2 account (see [[db-datalake]]) and store data there.

---

## Databricks Mounts

Mounting lets you "attach" an external storage location (ADLS, S3) to a DBFS path so you can access it using simple file paths instead of full `abfss://` URIs.

### Benefits
- Access data without embedding credentials in every notebook.
- Use familiar file-path semantics (`/mnt/mydata/`) instead of full storage URLs.
- Shared across all users on the workspace.

### How It Works
```
Databricks Notebook
      ↓
    DBFS mount  (/mnt/raw/)
      ↓
Service Principal (authentication via [[db-secrets|Key Vault]])
      ↓
Azure Data Lake Gen2
```

### Creating a Mount
```python
configs = {
    "fs.azure.account.auth.type": "OAuth",
    "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
    "fs.azure.account.oauth2.client.id": dbutils.secrets.get("scope", "client-id"),
    "fs.azure.account.oauth2.client.secret": dbutils.secrets.get("scope", "client-secret"),
    "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/<tenant-id>/oauth2/token"
}

dbutils.fs.mount(
    source="abfss://<container>@<storage-account>.dfs.core.windows.net/",
    mount_point="/mnt/raw",
    extra_configs=configs
)
```

### After Mounting
```python
df = spark.read.parquet("/mnt/raw/sales/2024/")
```

---

## Why Unity Catalog Replaced This

Mounts are workspace-scoped, hard to audit, and require per-workspace reconfiguration. Unity Catalog provides centralized, account-level governance with proper RBAC and lineage tracking. See [[db-sparksql]] for the Unity Catalog table model.

---

> Related: [[db-datalake]] (ADLS authentication), [[db-secrets]] (storing credentials for mounts), [[db-notebooks]] (`dbutils.fs` commands)

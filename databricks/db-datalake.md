---
tags: [databricks, azure, adls, storage, authentication]
aliases: [ADLS, Azure Data Lake, Data Lake Storage]
---

# Accessing Azure Data Lake Storage (ADLS)

## 1. Azure Storage Fundamentals

### Data Lake
A central repository for all data types (structured, semi-structured, unstructured) at any scale. Data is stored in raw format; structure is applied on read — **Schema-on-Read**.

### Storage Account
Groups all Azure Storage services together (Blobs, Files, Queues, Tables). Provides a unique namespace and is the basic building block for storage in Azure.

### ADLS Gen2
Azure Blob Storage with a "Big Data" upgrade.
- **Hierarchical Namespace:** Real folder structure (not just long filenames faking folders like standard Blob). This makes Spark jobs significantly faster for operations like rename/delete.

### Container
A "root folder" or partition within a storage account. You must create at least one container before uploading files.

---

## 2. Authentication Methods

### A. Storage Access Key ("Master Key")
Each storage account has two 512-bit access keys.
- **Permissions:** Full control — if someone has this, they have the keys to the kingdom.
- **Best Practice:** Store in **Azure Key Vault** (see [[db-secrets]]) so they never appear in notebook code.
- **Spark Config:**
  ```python
  spark.conf.set(
      "fs.azure.account.key.<storage-account>.dfs.core.windows.net",
      "<access-key>"
  )
  ```

### B. SAS Token (Shared Access Signature)
A string that grants limited, temporary access.
- Set an expiration date and specific permissions (e.g., "Read only for 2 hours").
- Good for sharing access with external parties without exposing the master key.

### C. Service Principal ("Robot User")
The standard for production environments. Think of it as a dedicated service account for your Databricks cluster.

| Field | What it is |
| :--- | :--- |
| **Application (Client) ID** | The "Username" of the robot |
| **Directory (Tenant) ID** | Your Azure account/tenant ID |
| **Client Secret** | The "Password" of the robot |

> Store the Client Secret in [[db-secrets\|Azure Key Vault]], never hardcoded.

### D. AAD Passthrough
Uses your own Azure Active Directory credentials. Databricks "passes" your identity to the storage account — access is controlled by your personal RBAC permissions, not shared credentials.

### E. Unity Catalog (Modern Approach)
Define a **Storage Credential** in Unity Catalog and grant access via SQL:
```sql
GRANT READ ON STORAGE CREDENTIAL my_credential TO `user@company.com`;
```
No credential management in notebooks. The cluster handles the handshake automatically. **Preferred for new workspaces.**

---

## 3. Connecting: The ABFS Driver

Databricks uses the **ABFS (Azure Blob File System)** driver to communicate with ADLS Gen2 over HTTPS.

### URI Format
```
abfss://<container>@<storage-account>.dfs.core.windows.net/<path>/
```
- **`abfss`** — the `s` = Secure (SSL/TLS encrypted)
- **`dfs`** — uses the Data Lake Gen2 endpoint (not the legacy Blob endpoint)

---

## 4. Configuration Scopes

| Scope | Behavior |
| :--- | :--- |
| **Notebook-level** | Access lasts only while the notebook is attached to the cluster |
| **Cluster-level** | Added to Spark config; every notebook on that cluster inherits access. Not recommended when different teams need different access levels. |
| **Unity Catalog** | Access governed by SQL grants — no per-cluster or per-notebook config needed |

---

> **Tip:** Getting `403 Forbidden`? 90% of the time the Service Principal is missing the **"Storage Blob Data Contributor"** role in the Azure Portal IAM settings.

> Related: [[db-secrets]] (storing credentials), [[db-dbfs]] (legacy mount approach), [[db-sparksql]] (querying data via SQL)

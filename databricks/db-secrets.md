---
tags: [databricks, security, secrets, keyvault]
aliases: [Secret Scopes, Databricks Secrets, Key Vault]
---

# Securing Secrets in Databricks

Databricks **Secret Scopes** let you store credentials (API keys, passwords, SAS tokens) securely. Instead of hardcoding sensitive values, you reference them by name — the actual value is never exposed in notebook output.

---

## 1. Secret Scope Types

| Feature | Databricks-Backed Scope | Azure Key Vault-Backed Scope |
| :--- | :--- | :--- |
| **Management** | Managed entirely by Databricks | Managed in Azure Key Vault |
| **Best For** | Standalone Databricks environments | Azure-native architectures |
| **Creation** | Databricks CLI or Secrets REST API | Azure Portal → linked to Databricks |

**Azure Key Vault-backed scopes are preferred** in Azure environments because secrets are managed centrally and can be rotated without touching Databricks configuration.

---

## 2. Accessing Secrets in Notebooks

Use `dbutils.secrets.get()`. The returned value is **always redacted** in cell output — it will show `[REDACTED]` if printed.

```python
# Syntax: dbutils.secrets.get(scope="scope-name", key="secret-key")
db_password = dbutils.secrets.get(scope="production-vault", key="sql-password")

# List available scopes
dbutils.secrets.listScopes()

# List keys within a scope
dbutils.secrets.list("production-vault")
```

---

## 3. Secrets in Cluster Configuration

Inject secrets directly into a cluster's **Spark Config** or **Environment Variables**. This is useful for storage mounts or global credentials that should be available to all notebooks on the cluster.

### Spark Config Syntax
Use double-curly braces to reference a secret:
```
{{secrets/<scope-name>/<secret-name>}}
```

**Example** — setting a Service Principal key for ADLS Gen2 in Spark Config:
```
fs.azure.account.oauth2.client.secret.yourstorage.dfs.core.windows.net {{secrets/azure-scope/sp-client-secret}}
```

The cluster resolves the secret at startup; the actual value is never visible in the UI.

---

## 4. Creating a Secret Scope (CLI)

```bash
# Databricks-backed scope
databricks secrets create-scope --scope my-scope

# Add a secret
databricks secrets put-secret --scope my-scope --key my-key --string-value "my-value"

# Azure Key Vault-backed scope
databricks secrets create-scope \
  --scope my-akv-scope \
  --scope-backend-type AZURE_KEYVAULT \
  --resource-id /subscriptions/.../vaults/my-vault \
  --dns-name https://my-vault.vault.azure.net/
```

---

> Related: [[db-datalake]] (authenticating to ADLS), [[db-dbfs]] (using secrets for mounts), [[db-notebooks]] (`dbutils.secrets` usage)

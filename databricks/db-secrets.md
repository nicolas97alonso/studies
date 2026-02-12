# Securing Secrets in Databricks

Databricks **Secret Scopes** allow you to store credentials (API keys, passwords, SAS tokens) securely. Instead of hardcoding sensitive information, you reference these secrets in notebooks, clusters, and jobs.

---

## 1. Secret Scope Types

There are two primary ways to manage secret scopes in Databricks:

| Feature | Databricks-Backed Scope | Azure Key Vault-Backed Scope |
| :--- | :--- | :--- |
| **Management** | Managed entirely by Databricks. | Managed via Azure Key Vault. |
| **Best Practice** | Good for standalone Databricks environments. | **Preferred solution** for Azure-native architectures. |
| **Creation** | Created via Databricks CLI or Secrets API. | Created in Azure Portal and linked to Databricks. |

---

## 2. Accessing Secrets in Notebooks

To retrieve a secret within a notebook, use the `dbutils` utility. This ensures the secret is redacted (hidden) from the notebook output.

**Syntax:**
```python
# Usage: dbutils.secrets.get(scope="scope-name", key="secret-key")

db_password = dbutils.secrets.get(scope="production-vault", key="sql-password")
```


## 3. Accessing Secrets in Cluster Configurations

You can inject secrets directly into the **Spark Config** or **Environment Variables** of a cluster. This is useful for mounting storage or setting global credentials without exposing them in the UI.

### Spark Config Syntax
Use the **double-curly brace** syntax to reference a secret from a specific scope:
`{{secrets/<scope-name>/<secret-name>}}`

**Example:**
To set a service principal key in the Spark Config for ADLS Gen2:
```text
fs.azure.account.oauth2.client.secret.yourstorage.dfs.core.windows.net {{secrets/azure-scope/sp-client-secret}}

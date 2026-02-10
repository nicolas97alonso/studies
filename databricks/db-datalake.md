# Databricks: Accessing Azure Data Lake Storage (ADLS)

## 1. Azure Storage Fundamentals

### What is a Data Lake?
A **Data Lake** is a central repository that allows you to store all your data (structured, semi-structured, and unstructured) at any scale. Unlike traditional databases, you don't need to transform the data before saving it; you store it in its raw format and apply structure only when you read it ("Schema-on-read").

### What is a Storage Account?
An **Azure Storage Account** is a container that groups all of your Azure Storage services together (Blobs, Files, Queues, Tables). It provides a unique namespace for your data and is the basic building block for storage in Azure.

### What is Azure Data Lake Storage (ADLS) Gen2?
**ADLS Gen2** is essentially Azure Blob Storage with a "Big Data" upgrade. 
* **Hierarchical Namespace:** This is the killer feature. It allows the storage to have a real folder structure (directories). In standard blob storage, folders are just "faked" by long filenames. In Gen2, folders are real, which makes Spark jobs significantly faster when moving or deleting data.

### What is a Container?
A **Container** is like a "root folder" or a drive partition within your storage account. You must create at least one container before you can upload any files or folders.

---

## 2. Authentication Methods

### A. Storage Access Key (The "Master Key")
Each storage account comes with two 512-bit access keys.
* **Permissions:** Full control (Super User). If someone has this, they have the keys to the kingdom.
* **Best Practice:** Use **Azure Key Vault** to store these keys so they aren't visible in your code.
* **Spark Configuration:**
  ```python
  spark.conf.set(
    "fs.azure.account.key.<storage-account-name>.dfs.core.windows.net", 
    "<access-key>"
  )

### B. Shared Access Signature (SAS Token)
A **SAS token** is a string that provides limited, temporary access to your storage resources.
* **Granularity:** You can set an expiration date and choose exactly what the user can do (e.g., "Read only" for the next 2 hours).

---

## 3. The "Service Principal" (App Registration)
This is the standard for production but can be confusing. Think of a **Service Principal** as a "Robot User" for your Databricks cluster.

### The ID Cheat Sheet:
* **Application (Client) ID:** The "Username" for the robot.
* **Directory (Tenant) ID:** The ID of your specific Azure account/office.
* **Client Secret:** The "Password" for the robot.


## 4. Azure Active Directory (AAD) Passthrough
This method uses your own Azure credentials. When you run a command in a notebook, Databricks "passes" your identity to the storage account to check if you personally have permission to see the data.

---

## 5. Unity Catalog
This is the modern, "no-code" way to manage security.
* Instead of mounting drives or using secrets in notebooks, you define a **Storage Credential** in Unity Catalog.
* Users are granted access via SQL commands (e.g., `GRANT READ ON...`).
* The cluster handles the "handshake" with Azure automatically.

---

## 6. How to Connect: The ABFS Driver
Databricks uses the **ABFS (Azure Blob File System)** driver to talk to ADLS Gen2. It is optimized for big data and runs over HTTPS.

---

## Configuration Scopes:
* **Notebook Level:** The access lasts only as long as the notebook is attached to the cluster.
* **Cluster Level:** The config is added to the cluster settings, so every notebook on that cluster can access the data automatically.
  (Not widly use approach, different roles cant use the same cluster if the only need specefic access to data
  Go to cluster, edit, in the spark set up, use (key value) key separated by space then value

---

### The URI (Address) Format:
To point Spark to your data, use this specific format:
`abfss://<container-name>@<storage-account-name>.dfs.core.windows.net/<folder-path>/`

* **abfss:** The "s" stands for **Secure** (SSL/TLS).
* **dfs:** This tells Azure you are using the **Data Lake (Gen2)** endpoint, not the old Blob endpoint.

---

> **Pro-Tip:** If you're getting "403 Forbidden" errors, 90% of the time it's because the Service Principal hasn't been given the **"Storage Blob Data Contributor"** role in the Azure Portal!







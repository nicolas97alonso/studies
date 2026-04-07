---
tags: [databricks, notebooks, development, dbutils]
aliases: [Databricks Notebooks, Magic Commands, dbutils]
---

# Databricks Notebooks

Notebooks are the primary interactive development environment in Databricks. Each notebook is attached to a cluster and executes code cell by cell. Default language is Python, but you can switch per cell.

---

## Magic Commands

Magic commands change the behavior or language of a single cell. They start with `%`.

| Command | Purpose |
| :--- | :--- |
| `%python` | Run the cell as Python |
| `%sql` | Run the cell as Spark SQL |
| `%scala` | Run the cell as Scala |
| `%r` | Run the cell as R |
| `%md` | Render the cell as Markdown |
| `%fs` | Run DBFS file system commands (wraps `dbutils.fs`) |
| `%sh` | Run shell commands on the **Driver** node only |
| `%pip` | Install Python packages into the notebook environment |
| `%run` | Execute another notebook and import its variables/functions |

---

## The Three Environments

Understanding what each environment is helps avoid confusion:

| Environment | What it is | Example paths |
| :--- | :--- | :--- |
| **OS Filesystem** | Local disk of the Driver VM. Works like a normal Linux machine. | `/tmp/`, `/home/` |
| **DBFS** | Virtual filesystem backed by cloud storage (ADLS, S3). Shared across the cluster and persists after shutdown. | `dbfs:/mnt/raw/`, `/mnt/raw/` |
| **Python Environment** | The Python runtime your notebook runs in. Packages installed with `%pip` live here. | `import pandas` |

> **Rule of thumb:** Use DBFS (`/mnt/...`) for data files you want to persist. Use the OS filesystem only for temp files needed during a single run.

---

## Importing Other Notebooks

```python
# Relative path (same folder)
%run ./utils

# Move up a folder
%run ../shared/config
```

After `%run`, all variables and functions defined in the called notebook are available in the current one.

---

## Databricks Utilities (`dbutils`)

`dbutils` is a Python object pre-loaded in every notebook. It provides utilities for working with files, secrets, and widgets — things you can't easily do with magic commands alone.

```python
dbutils.help()           # list all utility groups
dbutils.fs.help()        # list file system commands
```

### File System Utilities (`dbutils.fs`)

```python
dbutils.fs.ls("/mnt/raw/")           # list files and folders
dbutils.fs.mkdirs("/mnt/raw/new/")   # create a directory
dbutils.fs.cp("source", "dest")      # copy a file
dbutils.fs.rm("path", recurse=True)  # delete (recurse for folders)
```

`display()` renders the list as a formatted table instead of raw Python output:

```python
items = dbutils.fs.ls("/databricks-datasets/")
display(items)

# Count folders vs files
folder_count = len([i for i in items if i.name.endswith("/")])
file_count   = len([i for i in items if not i.name.endswith("/")])
```

### Secrets Utilities (`dbutils.secrets`)

```python
# Retrieve a secret (value is redacted in output)
password = dbutils.secrets.get(scope="my-scope", key="db-password")
```

> See [[db-secrets]] for how to set up Secret Scopes.

### Widget Utilities (`dbutils.widgets`)

Widgets create interactive input controls in the notebook UI — useful for parameterizing notebooks used as jobs.

```python
dbutils.widgets.text("environment", "dev", "Environment")
env = dbutils.widgets.get("environment")
```

### Notebook Utilities (`dbutils.notebook`)

```python
# Run another notebook and capture its return value
result = dbutils.notebook.run("./child-notebook", timeout_seconds=60, arguments={"key": "value"})
```

---

## Magic Commands vs. `dbutils`

| Use Case | Choose |
| :--- | :--- |
| Quick, one-off file browsing or SQL query | Magic command (`%fs`, `%sql`) |
| Parameterized, reusable, production code | `dbutils` |
| Passing values between notebooks | `dbutils.notebook.run()` |
| Installing packages | `%pip install ...` |

---

> Related: [[db-spark]] (SparkSession in notebooks), [[db-dbfs]] (DBFS mounts), [[db-secrets]] (using secrets in notebooks)

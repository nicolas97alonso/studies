---
tags: [databricks, notebooks, development, dbutils]
aliases: [Databricks Notebooks, Magic Commands, dbutils]
---

# Databricks Notebooks

Notebooks are the primary interactive development environment in Databricks. Each notebook is attached to a cluster and executes code cell by cell.

---

## 1. Magic Commands

Change the language or behavior of a single cell with `%` prefix.

| Command | Purpose |
|:---|:---|
| `%python` | Run cell as Python |
| `%sql` | Run cell as Spark SQL |
| `%scala` | Run cell as Scala |
| `%r` | Run cell as R |
| `%md` | Render cell as Markdown |
| `%fs` | DBFS file system commands (shorthand for `dbutils.fs`) |
| `%sh` | Shell commands on the **Driver node only** (not distributed) |
| `%pip` | Install Python packages into the notebook environment |
| `%run` | Execute another notebook and import its variables/functions |

> [!note] `%sh` vs `%fs`
> `%sh` runs OS-level shell commands on the Driver VM. `%fs` operates on DBFS (the distributed file system). They are completely different namespaces.

---

## 2. The Three Environments

| Environment | What it is | Example paths |
|:---|:---|:---|
| **OS Filesystem** | Local disk of the Driver VM | `/tmp/`, `/home/ubuntu/` |
| **DBFS** | Virtual filesystem backed by cloud storage (shared, persists after cluster restart) | `dbfs:/mnt/raw/`, `/mnt/raw/` |
| **Python Environment** | The Python runtime (packages installed with `%pip`) | `import pandas` |

> [!tip] Use DBFS/`/mnt/...` for any data you want to persist. Use the OS filesystem only for temp files needed within a single run.

---

## 3. `%run` — Import Another Notebook

```python
# Relative path (same folder)
%run ./utils

# Move up a folder
%run ../shared/config
```

After `%run`, all variables and functions defined in the called notebook are in scope. There is **no return value** — it's like a Python import.

> [!note] `%run` vs `dbutils.notebook.run()`
> `%run` — imports variables, runs synchronously, used for sharing code.
> `dbutils.notebook.run()` — runs a notebook as a sub-task, captures return value, can run in parallel.

---

## 4. `dbutils` — Databricks Utilities

Pre-loaded Python object in every notebook for file system ops, secrets, widgets, and notebook chaining.

```python
dbutils.help()       # list all utility groups
dbutils.fs.help()    # list file system commands
```

### `dbutils.fs` — File System

```python
dbutils.fs.ls("/mnt/raw/")              # list directory
display(dbutils.fs.ls("/mnt/raw/"))     # render as table

dbutils.fs.mkdirs("/mnt/raw/new/")      # create directory
dbutils.fs.cp("source/", "dest/", recurse=True)  # copy
dbutils.fs.mv("old/path", "new/path")  # move/rename
dbutils.fs.rm("/mnt/old/", recurse=True)  # delete
dbutils.fs.head("/mnt/file.csv", maxBytes=10000)  # preview file contents
```

### `dbutils.secrets` — Read Secrets

```python
password = dbutils.secrets.get(scope="my-scope", key="db-password")
# Note: printed value is always [REDACTED] — can't be leaked

dbutils.secrets.listScopes()              # available scopes
dbutils.secrets.list("my-scope")         # keys in a scope
```

### `dbutils.widgets` — Parameterize Notebooks

```python
dbutils.widgets.text("start_date", "2024-01-01", "Start Date")
dbutils.widgets.dropdown("env", "dev", ["dev", "staging", "prod"], "Environment")
dbutils.widgets.combobox("region", "us-east", ["us-east", "eu-west"])
dbutils.widgets.multiselect("tables", "orders", ["orders", "users", "products"])

start = dbutils.widgets.get("start_date")
dbutils.widgets.remove("start_date")
dbutils.widgets.removeAll()
```

### `dbutils.notebook` — Notebook Orchestration

```python
# Run a child notebook; returns its exit value
result = dbutils.notebook.run(
    "./child-notebook",
    timeout_seconds=300,
    arguments={"start_date": "2024-01-01"}
)

# Exit a notebook with a return value (readable by parent)
dbutils.notebook.exit("SUCCESS: 42 records processed")
```

### `dbutils.jobs` — Task Values (in Workflows)

```python
# Set a value to pass to downstream tasks
dbutils.jobs.taskValues.set(key="record_count", value=42)

# Retrieve from a previous task
count = dbutils.jobs.taskValues.get(taskKey="ingest_task", key="record_count", default=0)
```

---

## 5. Magic Commands vs. `dbutils`

| Use Case | Choose |
|:---|:---|
| Quick one-off file browsing | `%fs ls /mnt/raw/` |
| Parameterized production code | `dbutils.fs.ls()` |
| Passing values between notebooks | `dbutils.notebook.run()` + `dbutils.notebook.exit()` |
| Installing packages | `%pip install <package>` |
| Reading secrets | `dbutils.secrets.get()` |

---

## 6. Git Integration

Databricks notebooks can be synced with a Git repository (GitHub, GitLab, Azure DevOps).

**Two modes:**
- **Databricks Repos (legacy):** Import a Git repo into the workspace. Edit notebooks in Databricks, commit/push from the Repos UI.
- **Git Folders (current):** Same concept, newer name. Lets you sync individual files, not just full repos.

```python
# In a notebook, check if running from a Git repo:
# Git context shows the branch name in the notebook header
```

> [!tip] Exam context: Repos/Git Folders allow version-controlled notebooks to be used in Jobs as notebook tasks, making pipelines reproducible and deployable from CI/CD.

---

## 7. Notebook-scoped Libraries

`%pip install` installs packages for the **current notebook session only** — other notebooks on the same cluster are not affected.

```python
# Install a specific version
%pip install pandas==2.1.0 great-expectations

# Install from a private feed
%pip install --extra-index-url https://myfeed.example.com/pypi mypackage

# Restart Python after pip install (auto-happens in newer DBR, manual in older)
dbutils.library.restartPython()
```

> [!warning] Exam trap: `%pip` vs cluster-level libraries
> `%pip` = notebook-scoped, session only. Cluster-level libraries (installed via the cluster UI or `init scripts`) = available to ALL notebooks on the cluster. If the exam asks "how to install a library only for one notebook", the answer is `%pip`.

---

## 8. Practice Questions

**Q1.** What is the difference between `%run ./utils` and `dbutils.notebook.run("./utils")`?
> **Answer:** `%run` executes synchronously and **imports all variables and functions** from the target notebook into the current scope — like a Python import. `dbutils.notebook.run()` runs the notebook as a **sub-process**, captures only its exit value (string), and can run with a timeout. Use `%run` for shared utility code; use `dbutils.notebook.run()` for orchestration.

**Q2.** A `%sh` command lists files using `ls /tmp/`. Is this the same as `%fs ls /tmp/`?
> **Answer:** No — completely different. `%sh` runs on the Driver VM's local OS filesystem. `%fs` operates on DBFS (a distributed virtual filesystem backed by cloud storage). `/tmp/` in `%sh` is temporary Driver local disk; `/tmp/` in `%fs` is DBFS.

**Q3.** You install a package with `%pip install seaborn` in Notebook A. Can Notebook B on the same cluster use seaborn?
> **Answer:** No — `%pip` is notebook-scoped. For cluster-wide packages, install them in the cluster configuration (Libraries tab) or use a cluster init script.

**Q4.** A notebook calls `dbutils.widgets.get("start_date")` but no widget was created. What happens?
> **Answer:** If a value was passed as a job parameter with that key, it returns that value. If no value was set anywhere, it throws an `InputWidgetNotDefined` error. Always use a default: `dbutils.widgets.text("start_date", "2024-01-01")`.

**Q5.** You need to run three notebooks in parallel and wait for all to finish. How?
> **Answer:** Use `dbutils.notebook.run()` calls in separate Python threads or use a Databricks Job with multiple parallel notebook tasks (parallel tasks in the workflow DAG). `%run` is synchronous and can't be parallelized.

---

> Related: [[db-spark]] (SparkSession in notebooks), [[db-dbfs]] (DBFS mounts), [[db-secrets]] (setting up secret scopes)

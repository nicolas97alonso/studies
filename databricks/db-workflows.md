---
tags: [databricks, workflows, jobs, orchestration, exam-priority]
aliases: [Databricks Jobs, Workflows, Job Clusters, Orchestration]
---

# Databricks Workflows & Jobs

> [!important] Exam Priority: HIGH
> Job Clusters vs All-Purpose Clusters is a very common exam question. Also know: task types, dependencies, and repair runs.

Workflows is the Databricks orchestration layer for running automated pipelines. A **Job** is the scheduling unit; it contains one or more **Tasks**.

---

## 1. Jobs vs. All-Purpose Clusters (Exam Classic)

| Feature | All-Purpose Cluster | Job Cluster |
|:---|:---|:---|
| **Lifecycle** | Lives until you stop it | Created at job start, terminated when job ends |
| **Cost** | Higher DBU rate | Lower (discounted) DBU rate |
| **Use case** | Interactive development | Production automated pipelines |
| **Sharing** | Multiple users | Isolated to one job run |
| **Startup time** | Instant (already running) | 3–7 min (VM provisioning) — use pools to reduce |

> [!tip] Production rule of thumb: always use Job Clusters for scheduled work. All-Purpose = dev/exploration.

---

## 2. Task Types

A job can contain multiple task types, mixed in the same job:

| Task Type | What it runs |
|:---|:---|
| **Notebook** | A Databricks notebook |
| **Python Script** | `.py` file from workspace or Git |
| **DLT Pipeline** | A Delta Live Tables pipeline |
| **Spark Submit** | JAR or Python on a cluster using spark-submit |
| **SQL** | A SQL query or dashboard refresh |
| **dbt** | A dbt project |
| **Run job** | Triggers another job (job chaining) |

---

## 3. Task Dependencies (DAG)

Tasks can run sequentially or in parallel by setting dependencies:

```
Task A
  ├── Task B (depends on A)
  │     └── Task D (depends on B)
  └── Task C (depends on A)
        └── Task D (depends on C too)
```

Databricks renders this as a visual DAG in the UI. Tasks with no dependencies in common run in parallel automatically.

---

## 4. Passing Data Between Tasks

```python
# In task 1: set a value
dbutils.jobs.taskValues.set(key="record_count", value=42)

# In task 2: retrieve it
count = dbutils.jobs.taskValues.get(
    taskKey="task_1_name",
    key="record_count",
    default=0
)
```

---

## 5. Parameters & Widgets

```python
# Notebook tasks receive parameters as widgets
dbutils.widgets.get("start_date")   # retrieve param passed from job config
```

Job parameters can be set in the UI or API, and override widget defaults at runtime.

---

## 6. Scheduling

| Schedule Type | Description |
|:---|:---|
| **Cron schedule** | Standard cron syntax (`0 9 * * MON-FRI`) |
| **File arrival trigger** | Start when new files land in a storage path |
| **Continuous** | Re-run as soon as the previous run completes |
| **Manual** | Run on demand |

---

## 7. Repair Run

When a multi-task job partially fails, you can **repair** it — rerun only the failed and downstream tasks, without re-running successful ones.

```
Job: A → B → C → D
              ↑ failed

Repair run: re-runs C and D only. A and B are skipped.
```

> [!important] Exam trap
> Repair run is only available for jobs with multiple tasks. It saves time and cost by not reprocessing already-successful tasks.

---

## 8. Job Run History & Monitoring

```python
# Programmatic job management via SDK
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
w.jobs.run_now(job_id=123)
```

In the UI: **Workflows → Job Runs** shows full history, logs, and repair options.

---

## 9. Alerts & Notifications

Configure per-job alerts for:
- Job start
- Job success
- Job failure
- Duration exceeded threshold

Destinations: email, Slack, PagerDuty, webhooks.

---

> Related: [[db-databricks]] (cluster types), [[db-dlt]] (DLT pipelines as job tasks), [[db-notebooks]] (notebook task development)

---

## 10. Retry Policies & Error Handling

Every task in a Databricks Job can have its own retry configuration:

```json
{
  "max_retries": 3,
  "min_retry_interval_millis": 60000,
  "retry_on_timeout": true
}
```

> [!warning] Retries don't help with bad code
> If a task fails due to a logic error or bad data, retrying won't fix it. Retries are for **transient infrastructure failures** (network blips, cluster startup failures), not code bugs.

Each task can also have a `timeout_seconds`. If exceeded, the task is marked failed (and retried if `retry_on_timeout = true`).

---

## 11. Job Permissions

Jobs have their own access control independent of notebook permissions:

| Permission | What it allows |
|:---|:---|
| `Can View` | See job runs and results |
| `Can Manage Run` | Trigger runs, cancel runs |
| `Can Edit` | Modify job configuration |
| `Is Owner` | Full control including delete |

> [!note] Run As Service Principal
> By default, a job runs as the owner's identity. Configure jobs to **run as a service principal** for production — this gives the job a stable, non-human identity that doesn't break if someone leaves the company.

---

## 12. Practice Questions

**Q1.** A 5-task job runs: A → B → C → D → E. Task C fails. Which tasks ran, and what does Repair Run re-execute?
> **Answer:** A and B completed. C failed; D and E never ran. Repair Run re-executes **C, D, and E** — the failed task and all downstream tasks that depend on it. A and B are skipped (already succeeded).

**Q2.** What is the key cost difference between All-Purpose and Job Clusters?
> **Answer:** Job Clusters have a **lower (discounted) DBU rate** — typically 40–75% cheaper. They also auto-terminate when the job ends, so you don't pay for idle time.

**Q3.** A job needs to pass a file count from Task 1 to Task 3. How?
> **Answer:** Task 1: `dbutils.jobs.taskValues.set(key="file_count", value=n)`. Task 3: `dbutils.jobs.taskValues.get(taskKey="task_1", key="file_count")`.

**Q4.** You want a job to start automatically whenever new files land in an ADLS container. Which schedule type?
> **Answer:** **File arrival trigger** — Databricks monitors the specified storage path and starts the job when new files are detected.

**Q5.** What happens to a Job Cluster after the job finishes?
> **Answer:** It's automatically terminated — VMs are released. This is the main difference from All-Purpose clusters, which stay running until manually stopped.

**Q6.** A notebook task calls `dbutils.notebook.run("./child", timeout_seconds=600)`. The child runs for 800 seconds. What happens?
> **Answer:** The child notebook is forcefully stopped at 600 seconds and the parent task receives a `NotebookExecutionTimeout` error, marking the task as failed.

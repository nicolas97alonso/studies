# 🚀 Databricks & Apache Spark Architecture: Enhanced Class Notes

## 1. Physical Infrastructure (Nodes & Clusters)
A **Node** is essentially a single Virtual Machine (VM). A Spark Cluster is a collection of these machines working together to solve a single problem.



### The Driver Node
The "Brain" of the operation. It runs the **Driver Program**.
* **The SparkSession (formerly SparkContext):** This is the heart of the Driver. It is the command center that translates your code into instructions, manages resource allocation, and tracks the state of the cluster.
* **Decision Making:** It decides how to split the workload (partitioning) and manages the distribution of tasks.
* **The Entry Point:** This is where the user interacts with the cluster.

### The Worker Nodes & Executors
Workers are the "Muscle" nodes.
* **Executor:** A distributed process responsible for executing the actual work (reading, writing, and processing). 
* **The Databricks Difference:** In a standard Spark environment, you can have multiple executors on a single worker node sharing resources. However, **Databricks restricts this to one Executor per Worker** for better performance stability.
* **Slots (Cores):** A slot is a unit of parallelism. 
    * **Can we limit the amount of cores?** Yes. You do this when configuring the cluster by selecting the "Worker Type." If you choose a VM with 4 cores, you have 4 slots. You can also use "Task Slots" configurations to limit concurrency if needed.
    * **The Logic:** Usually, **1 Slot = 1 CPU Core**. This is where your code's instructions are physically executed.

---

## 2. The Software Logic (DataFrames & APIs)

### What is a Spark DataFrame?
A DataFrame is a distributed table with rows, columns, and data types. 

* **Logical Partitioning:** Data is divided into "chunks" called partitions. 
    * **What is a Logical Partition?** It is a subset of your total data. If you have 1TB of data, Spark might split it into 1,000 partitions of 1GB each. This allows Spark to give a small piece of the "puzzle" to each slot so they can work in parallel.
* **Data Sinks:** * **What is a Data Sink?** If a "Source" is where data comes from (like a CSV or S3 bucket), a **Sink** is the destination where the data is written (like a Delta Table, a Database, or a Parquet file).

### Understanding the Spark "API"
* **Why is Spark called an API?** In this context, an **API (Application Programming Interface)** isn't a web URL (HTTP). It refers to the **Library** (Spark SQL, PySpark) that provides a set of pre-defined functions. It acts as a bridge: you write "User Friendly" code (like `.groupBy()`), and the Spark API translates that into complex "Distributed Machine" instructions.

---

## 3. The Execution Hierarchy (Jobs, Stages, Tasks)

When you run code in a Databricks Notebook (the **Application**), Spark breaks it down:

1.  **Job:** Triggered whenever you call an "Action" (e.g., `.save()`, `.collect()`, `.count()`).
2.  **Stage:** A Job is divided into Stages based on "Shuffle" boundaries.
    * **What is Shuffling?** This is the process of moving data across the network between different worker nodes. It happens when data from multiple partitions needs to be combined (like a `Join` or `GroupBy`). **Shuffling is the most expensive/slowest part of Spark.**
3.  **Task:** The smallest unit of work. One task is sent to **one slot** to process **one partition** of data.

---

## 4. Scaling and Capacity Planning

### Scaling Strategies
* **Vertical Scaling:** Increasing the "size" of the nodes (adding more RAM or Cores to the machine). You are limited by the maximum VM size available.
* **Horizontal Scaling:** Adding more Worker Nodes to the cluster. This is the "Spark Way" and is virtually unlimited.

### How to calculate how many workers I need?
There is no "one-size-fits-all," but use these guidelines:
* **The Data-to-RAM Ratio:** For optimal performance, your total Cluster RAM should be roughly **2x to 3x** the size of the dataset you are processing to avoid "spilling" to disk.
* **The Partition Rule:** Aim for **2-3 tasks per CPU core**. If your data is 10GB and you want 100MB partitions, you have 100 partitions. To process them efficiently, you’d want roughly 30-50 cores across your workers.
* **Worker Type Selection:**
    * **Memory Optimized VMs:** Best for large joins/shuffling.
    * **Compute Optimized VMs:** Best for complex transformations or Machine Learning.

---
---
---
---
# 🚀 Spark & API Fundamentals: A Beginner's Guide

## 1. SparkSession (The "Entry Point")
**The Question:** What is a SparkSession? How does it relate to SparkContext?

* **SparkSession:** This is your **Modern Control Panel**. Introduced in Spark 2.0, it is the only object you need to create to start writing Spark code. It allows you to read files, run SQL, and manage your data.
* **SparkContext:** This is the "Legacy Engine." In older versions (1.x), you had to use this directly. Today, the **SparkSession wraps the SparkContext inside it**, so you don't have to worry about the low-level details.
* **The Analogy:** If Spark is a massive factory, the **SparkSession** is the **Site Manager**. You give orders to the manager, and the manager coordinates all the workers for you.



---

## 2. Data Shuffling
**The Question:** What exactly is "shuffling"?

* **Definition:** Shuffling is the physical process of moving data across the network between different machines (Nodes) in a cluster.
* **When it happens:** It occurs during **"Wide Transformations"** like `groupBy`, `join`, or `sort`. 
    * *Example:* If you want to count every "Red" car in a massive dataset, Spark might have some "Red" car data on Server A and some on Server B. It has to **shuffle** (move) that data to one single place to count them together.
* **The Problem:** Shuffling is the **most expensive** operation in Spark. It uses network bandwidth, disk space, and time. Good Spark code tries to minimize shuffling.



---

## 3. Memory & Distribution
**The Question:** Does the Driver load everything? Where is the data stored?

* **The Driver (The Brain):** Does **NOT** load the data. It only stores the "Execution Plan" (the instructions) and coordinates the workers. If you try to load 1TB of data into the Driver, it will crash with an `OutOfMemoryError`.
* **The Executors (The Muscle):** These are the worker machines. They load the actual data into their **RAM (Memory)**.
* **Partitions:** Spark breaks your large files into small chunks called **Partitions**. 
    * If you have a 1GB file, Spark might split it into 8 chunks of 128MB.
    * Each Executor takes a few chunks, processes them, and clears them from memory.
* **Spilling:** If the RAM on an Executor gets too full, Spark "spills" the data to the **local hard drive** of that specific worker to prevent the program from crashing.



---

## 4. Why is PySpark an "API"?
**The Question:** I only know HTTP APIs. Why is PySpark called an API?

An **API (Application Programming Interface)** is simply a "contract" that lets two pieces of software talk to each other. 

| Feature | Web API (HTTP) | Library API (PySpark / Polars) |
| :--- | :--- | :--- |
| **How it connects** | Over the Internet (URL) | Locally in your code (`import`) |
| **Language** | JSON / XML | Python Methods / Objects |
| **The Bridge** | HTTP Protocol | Py4J (A local bridge between Python & Java) |
| **Analogy** | Ordering pizza on a website. | The buttons and labels on a microwave. |

* **Polars is also an API:** It is a **DataFrame API**. When you use `pl.DataFrame()`, you are using the Polars "contract" to talk to a high-speed engine written in the Rust programming language.



---

## 5. Summary Cheat Sheet

| Term | Simplified Definition |
| :--- | :--- |
| **SparkSession** | Your "Remote Control" for Spark. |
| **Executor** | The worker machines where the data lives. |
| **Shuffle** | Moving data between machines (Slow/Expensive). |
| **Partition** | A small "slice" of your total data. |
| **Py4J** | The hidden bridge that lets Python talk to Spark's Java engine. |

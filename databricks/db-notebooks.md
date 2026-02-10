### Notebooks
Interactive way to execute code, by defaoult is python language, it needs to be atached to a cluster

## Magic commands

%python, %sql, % scala Change language
%md Markdown file
%fs Run file system commands
%sh Run shell command (only on driver)
%pip pip install libs
%run include import other notebooks into current 

OS filesystem
This is the local disk of the driver machine in your cluster.
It works like any normal Linux computer.
Commands like cd, ls, and cat operate here.

DBFS (Databricks File System)
This is Databricks’ virtual filesystem that sits on top of cloud storage (S3, ADLS, GCS).
It’s shared across the whole cluster and persists even when the cluster shuts down.
It uses paths like dbfs:/mnt/....

Python environment
This is the Python runtime that your notebooks use.
It’s separate from the OS-level Python installation.
Packages installed with %pip go here so your notebook can import them.


To import modeuls you can use relative path with ./path 
or use ../path if you want to move back in folders

?? What is the dbfs so my data is stored in there , and data bricks partion there and use sql on top ???? im confused with that

## Databricks Utilities 

Only can run python, scala or R cells
More flesible then magic commands 

### File System Utilities 
dbutils.fs.ls('/') display the files like ls 
display() can display or pase the python list into a proper table 

Example:

items = dbitils.fs.ls('/databricks-datasets/')
folder_count = len(item for item in items if item.name.endswith("/")
file_count = len(item for item in items if not  item.name.endswith("/")


### Secrete Utilities 

### Widget Utilities

### Notebook ststen ubilities

* View all utilities = dbutils.help()
dbututils.fs.help()

Magic Command vs Utilities 

Magic command for quick adhock, utilities for parametrazation and production tuntime execution, programatically use case 

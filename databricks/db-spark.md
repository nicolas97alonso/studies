### Spark Arch

## Node 
A node a is a machine basically 

there are 

### Driver Node


### Worker node 


                  Driver Node 
                      VM 
                Core       Core
                Core       Core

 Worker Node                  Worker Node  
     VM                           VM 
Core       Core               Core      Core
Core       Core               Core      Core

In databricks the driver node have the driver program and create the spark context
What is spark context??
Drives decision like spliting work load, managing resources

Theere are the worker nodes 
The ones that are going to perfm the work also called executor

On a normal spark envoriment there can be one or more executor on a worker node sharing resources, but databricks restric to only one per worker, 

Executor does read a write as well as procesing

Each executor have slot

        Worker
        Executor
Slot            Slot  
Slot            Slot 

Usally the are the same numbers as cores
Slot are where the instuctions are executed


The driver node act as applicarion
Aplication have job, stage and task (didnt understand application, job task :()
Spark try to parelellize as much at it cans, this depend on how the data is partinioned 
The driver then asign the task to the slot to execute, then it return the result to the driver then to the user 

Scaling ///init

Nodes with more cores - Vertical scaling 
Limtimng to amount of cores per machine 

Add more workers - Horzontally 





## Spark DataFrame 
Rows and columns with datatypes, then is divided by logical partition (what is logival partition) then to be distrubted to the slots
This give spark to give small task to parellixe and be more faster 
Spark offer api datadrame to read data from a number data fromats 
Once the data is in df, it need to be transfored , spark offer several calucaltion 
Finally the data to be wirte, spark aslo offer api (What is data sink)


??? Can we limit the amount of cores???
?????? How to calculutae hoe many workers i need?????? per gm of my data set also what worker type????
???? Why there spark is an api???? all my life i think api as http apis, im lost with what is api in this case??

### Acess Azure Data Lake 


## What is a data lake 
Pleae complete 

## What is a storage account on azure 

## What is a datalake gen2 in azure 

## What is a container in a storage account in azure 

## Creating a storage account 
....... fORGOT TO WRITE THIS PART JK:WRITEP


Usally on azure data brciks we use azure data lake gen2 

## Storage Access Key
(super user)
azure recommend using key vaoult 

Each storage account comes with 2  keys 
Gives full access to the storage account 

we can use spark.config.set("fs.azaure.account.key.<storage-account>.dfs.core.windoes.net", "<aceess key>")

## Shared Acess Signature (SAS Token) 

More granular auth 

- Each of this can 

### Atach to the notobook
The session will be terminated when the notebook disatached from the cluster 

### Attach to the cluster
The session will initailize when the clsuter is spining and will end when it ends 

## Azure Active Directory (service principal)

Can use 

### AAD Passthtoigh Athentiiationation 

Uses the account of the person using the notebook and check for the roles

### Unity Catalog 

The cluster check in the unity catalog, if the use have permission will give the entrass if not, not 


## How to access
Ussay we connect to data lake using http
Databricks recomns abfs // what the f is this no idea


example 

abfs[s]://container@storage_account_name.dfs.core.windoes.net/ optional folder_path/file_name 









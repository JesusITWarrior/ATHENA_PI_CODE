import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime
import json
import config
import io
# make sure to run "python -m pip install azure-cosmos" before coding!

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']
AUTH_ID = config.settings['container_id_auth']
try:
    with open("/home/pi/Athena Data/Guid.txt","r") as f:
        GUID = f.read()
        f.close()
except:
    GUID = ""
    
def initConnection():
    global client
    global database
    global container
    client = cosmos_client.CosmosClient(HOST,{'masterKey':MASTER_KEY},user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    try:
        try:
            database = client.create_database(id=DATABASE_ID)
        except exceptions.CosmosResourceExistsError:
            database = client.get_database_client(DATABASE_ID)
        try:
            container = database.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
        except exceptions.CosmosResourceExistsError:
            container = database.get_container_client(CONTAINER_ID)
        
        return container
        
    except exceptions.CosmosHttpResponseError as e:
        print('Uh oh, failed to connect! {0}'.format(e.message))
        return None

def logData(temp, status, picture):
    now = datetime.datetime.now()
    print("LOGGED TO {}".format(GUID))
    jsonNow = json.dumps(now, default=str)
    jsonNow = jsonNow.replace("\"", "")
    statusLocal = [
        {
            "dataName": "Temperature",
            "value" : temp
        },
        {
            "dataName": "Door Open Status",
            "value" : status
        },
        {
             "dataName": "Picture",
             "value": picture
         }
    ]

    statusDB = {
        "id": "{} Status".format(GUID),
        "updatedTime": jsonNow,
        "loggedstatus": statusLocal
    }
    
    try:
        container.create_item(body=statusDB)
    except exceptions.CosmosResourceExistsError:
        container.replace_item(item=statusDB["id"], body=statusDB)
        
def fetch_guid(username, password):
    global GUID
    print(username+" "+password)
    i = 0
    while i < 10:
        try:
            client = cosmos_client.CosmosClient(HOST,{'masterKey':MASTER_KEY},user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
            break
        except Exception as clientOOF:
            print(clientOOF)
            i += 1
            sleep(0.25)
        
    print("Got client: {}".format(client))
    try:
        try:
            database = client.create_database(id=DATABASE_ID)
        except exceptions.CosmosResourceExistsError:
            database = client.get_database_client(DATABASE_ID)
        print("Got database: {}".format(database))
        try:
            container = database.create_container(id=AUTH_ID, partition_key=PartitionKey(path='/partitionKey'))
        except exceptions.CosmosResourceExistsError:
            container = database.get_container_client(AUTH_ID)
        print("Got container: {}".format(container))
    except Exception as DBOOF:
        print(DBOOF)
        return None
    account_info = container.read_item(item=username, partition_key=username)
    if account_info["id"] == username and account_info["password"] == password:
        GUID = account_info["key"]
        print("GUID = {}".format(GUID))
        return account_info["key"]
    else:
        return False
# client = cosmos_client.CosmosClient(HOST,{'masterKey':MASTER_KEY},user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
# try:
#     try:
#         database = client.create_database(id=DATABASE_ID)
#     except exceptions.CosmosResourceExistsError:
#         database = client.get_database_client(DATABASE_ID)
#     try:
#         container = database.create_container(id=AUTH_ID, partition_key=PartitionKey(path='/partitionKey'))
#     except exceptions.CosmosResourceExistsError:
#         container = database.get_container_client(AUTH_ID)
#     
# except exceptions.CosmosHttpResponseError as e:
#     print('Uh oh, failed to connect! {0}'.format(e.message))

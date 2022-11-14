import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime
import json
import config
import io
from uuid import uuid4
from time import sleep
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
    
try:
    with open("/home/pi/Athena Data/Uuid.txt", "r") as f:
        pic_uuid = f.read()
        f.close()
except:
    pic_uuid = ""
    
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

def log_status(temp, door):
    now = datetime.datetime.now()
    json_now = json.dumps(now, default=str)
    json_now = json_now.replace("\"","")
    local_status = {
        "id": str(uuid4()),
        "accountID": GUID,
        "recordType": "status",
        "updatedTime": json_now,
        "Temperature": temp,
        "DoorOpenStatus": door
    }
    
    #Add wifi fixing here...
    #with open("/home/pi/Athena Data/loggedData.json", "w") as testfile:
        #testfile.write(json.dumps(statusDB))
        #testfile.close()
    
    try:
        container.create_item(body=local_status)
        if path.exists("/home/pi/Athena Data/loggedData.json"):
            #Convert from JSON and log the data
            print("Updating database with old values...")
            local_file = open("/home/pi/Athena Data/loggedData.json")
            local_data = json.load(local_file)
            local_file.close()
            for entry in local_data:
                error = True
                while error:
                    try:
                        print("Updating...")
                        container.create_item(body=entry)
                        error = False
                    except:
                        print("Another error")
                        error = True
            os.remove("/home/pi/Athena Data/loggedData.json")
                
    except Exception as BIGOOF:
        print("ERROR: {}".format(BIGOOF))
        try:
            Retry_Wifi()
            Check_Wifi()
            if not path.exists("/home/pi/Athena Data/loggedData.json"):
                temp_status = []
                temp_status.append(local_status)
                with open("/home/pi/Athena Data/loggedData.json", "w") as temp_files:
                    json.dump(temp_status, temp_files)
                    temp_files.close()
            else:
                f = open("/home/pi/Athena Data/loggedData.json")
                oldFile = json.load(f)
                f.close()
                oldFile.append(local_status)
                with open("/home/pi/Athena Data/loggedData.json", "w") as temp_files:
                    json.dump(oldFile, temp_files)
                    temp_files.close()
                
        
def log_picture(picture):
    now = datetime.datetime.now()
    json_now = json.dumps(now, default=str)
    json_now = json_now.replace("\"","")
    local_picture = {
        "id": pic_uuid,
        "accountID": GUID,
        "recordType": "picture",
        "updatedTime": json_now,
        "Picture": picture
    }
    
    try:
        container.create_item(body=local_picture)
    except exceptions.CosmosResourceExistsError:
        try:
            container.replace_item(item=local_picture["id"], body=local_picture)
        except:
            print("Something happened...")
            
def Retry_Wifi():
    subprocess.check_output('sudo wpa_cli -i wlan0 reconfigure', shell = True)
    
def Check_Wifi():
    i = 0
    LINE_UP = '/033[1A'
    LINE_CLEAR = '/x1b[2K'
    print("Checking WiFi Connection...")
    while i <= 30:
        #This doesn't account for website requiring logins
        print('\r',"Attempting Connection... {}".format(i), sep='',end='',flush = True)
        try:
            result = subprocess.check_output('sudo iwgetid', shell = True)
            if result is not None:
                print('')
                return True
            else:
                sleep(1)
                i = i + 1
        except:
            sleep(1)
            i = i + 1
    print('')
    return False

def fetch_guid(username, password):
    global GUID
    global client
    global database
    global pic_uuid
    print(username+" "+password)
    i = 0
    while i < 40:
        try:
            client = cosmos_client.CosmosClient(HOST,{'masterKey':MASTER_KEY},user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
            break
        except Exception as clientOOF:
            print("Azure failed: {}".format(clientOOF))
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
        if account_info["picUUID"] == None:
            pic_uuid = str(uuid4())
            account_info["picUUID"] = pic_uuid
            update_with_uuid(account_info)
        else:
            pic_uuid = account_info["picUUID"]
        with open("/home/pi/Athena Data/Uuid.txt","w") as UUID:
            UUID.write(pic_uuid)
            UUID.close()
        print("GUID = {}".format(GUID))
        return account_info["key"]
    else:
        return False
    
def update_with_uuid(account_info):
    try:
        container = database.create_container(id=AUTH_ID, partition_key=PartitionKey(path='/partitionKey'))
    except exceptions.CosmosResourceExistsError:
        container = database.get_container_client(AUTH_ID)
        
    try:
        container.replace_item(item=account_info["id"], body=account_info)
    except Exception as BIGOOF:
        print("UUID failed!!!")
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

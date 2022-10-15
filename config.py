import os

settings={
    'host':os.environ.get('ACCOUNT_HOST', 'https://capstonetamu.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', 'qOCK60HdQU4oEJx2xop6D4DI4tqXu7EotJxvoOuUFH6DKJlDf546ZHH8aHAEM6CEtm4r5rc0MrEm0BA2HO90jQ=='),
    'database_id': os.environ.get('COSMOS_DATABASE', 'Global'),
    'container_id':os.environ.get('COSMOS_CONTAINER', 'ReportedData'),
    'container_id_auth':os.environ.get('COSMOS_CONTAINER','AuthBase')}
from dotenv import load_dotenv
import os
from azure.cosmos import CosmosClient

# enter credentials
load_dotenv()
account_endpoint = os.getenv("AccountEndpoint")
account_key = os.getenv("AccountKey")
database_name = os.getenv("DatabaseName")
container_name = os.getenv("ContainerName")

# Create a Cosmos client
client = CosmosClient(account_endpoint, account_key)

# Get a reference to the database
database = client.get_database_client(database_name)

# Get a reference to the container
container = database.get_container_client(container_name)

# Query all documents in the container
# query = "SELECT * FROM c"
# items = container.query_items(query=query, enable_cross_partition_query=True)

def create_user(user_name, email, pfp, playlist):    
    query = "SELECT * FROM c"
    items = container.query_items(query=query, enable_cross_partition_query=True)
    
    if user_name not in items:
        user_document = {
            'context_counter': 0,
            'user_name': user_name,
            'email': email,
            'pfp': pfp,
            'playlist': playlist
        }
    
    else:
        for user_name in user_document:
            context_counter += 1

    

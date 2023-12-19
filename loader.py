from dotenv import load_dotenv
import os
from azure.cosmos import CosmosClient, exceptions
from uuid import uuid4  # Import uuid4 to generate a unique identifier


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


def create_user(user_name, email, pfp, playlist):
    user_document = {
        'id': str(uuid4()),  # Generate a unique identifier
        'context_counter': 0,
        'user_name': user_name,
        'email': email,
        'pfp': pfp,
        'playlist': playlist
    }
    return user_document


def check_if_user_exist(username):
    query = f"SELECT * FROM c WHERE c.user_name = '{username}'"
    try:
        items = container.query_items(query=query, enable_cross_partition_query=True)
        
        for item in items:
            # Extract relevant data from the item
            existing_user = {
                'context_counter': item['context_counter'],
                'user_name': item['user_name'],
                'email': item['email'],
                'pfp': item['pfp'],
                'playlist': item['playlist']
            }

            # User already exists, retrieve context_counter and create an object
            existing_user['context_counter'] += 1
            return existing_user['context_counter']
        
        # User doesn't exist, create a new user
        return 0
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error while querying Cosmos DB: {e}")
        return -1  # Error code indicating failure


def create_new_item(item):
    try:
        container.create_item(body=item)
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error while creating item in Cosmos DB: {e}")

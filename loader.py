from dotenv import load_dotenv
import os
from azure.cosmos import CosmosClient, exceptions


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


def create_user(user_id, email, user_name, pfp, playlist):
    user_document = {
        'id': user_id,
        'User_id': email,
        'Signin_name': user_name,
        # '_rid': '', uniquely identify the document
        # '_self': f'', link to acces itself
        # '_etag': '', optimistic concurrency control
        # '_attachments': 'attachments/',
        'Partition_key': user_id,
        # '_ts': 1703624279, Timestamp
        'context_counter': 0,
        'pfp': pfp,
        'playlist': playlist,
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


def delete_user(user_id):
    try:
        # Query for the item to be deleted
        query = f"SELECT * FROM c WHERE c.id = '{user_id}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))

        # Check if the item exists
        if items:
            item = items[0]

            # Get the partition key dynamically
            partition_key = item.get('_partitionKey') or item.get('_rid') or item.get('_self')

            # Delete the item
            container.delete_item(item['id'], partition_key=partition_key)

            print(f"User '{user_id}' deleted successfully.")
        else:
            print(f"User '{user_id}' not found.")

    except Exception as e:
        print(f"Error deleting user '{user_id}': {e}")


def print_all_user_ids_and_usernames():
    query = "SELECT c.id, c.partition_key, c.user_name FROM c"
    items = container.query_items(query=query, enable_cross_partition_query=True)

    for item in items:
        user_id = item.get('id', 'N/A')
        username = item.get('user_name', 'N/A')
        print(f"User ID: {user_id}, Username: {username}")


def print_user_details_by_id(user_id):
    query = f"SELECT * FROM c WHERE c.id = '{user_id}'"
    result_iterable = container.query_items(query=query, enable_cross_partition_query=True)

    for item in result_iterable:
        print(f"User ID: {user_id}")
        for field, value in item.items():
            print(f"{field.capitalize()}: {value}")

from dotenv import load_dotenv
import os
from azure.cosmos import CosmosClient, exceptions
import uuid

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


def generate_uuid():
    return str(uuid.uuid4())


def create_user(unique_id, email, user_name, pfp, playlist):
    user_document = {
        'id': unique_id,  # unique id (internal need)
        'user_id': email,  # unique id (external need)
        'user_name': user_name,
        # '_rid': '',  uniquely identify the document
        # '_self': f'',  link to acces itself
        # '_etag': '',  optimistic concurrency control
        # '_attachments':  'attachments/',
        'partition_key': unique_id,
        # '_ts': 1703624279,  Timestamp
        'context_counter': 0,
        'pfp': pfp,
        'playlist': playlist,
    }
    return user_document


fobbiden_fields = {
    'id', '_rid', '_self', '_etag', 'partition_key', '_ts'
}


# Not tested yet
def update_user_playlist(playlist, context):
    updated_playlist = playlist.update(context)
    return updated_playlist


def edit_user(user_id, field_to_edit, new_value):

    if field_to_edit in fobbiden_fields:
        print(f"Field '{field_to_edit}' is not editable.")
        return -1  # Error code indicating failure
    
    query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    
    if items:
        # Assuming there's only one item with the given user_id
        user_item = items[0]
        
        print(f"Original Document: {user_item}")

        # Check if the field already exists in the user item
        if field_to_edit in user_item:
            # Update the existing field
            if field_to_edit == 'playlist':
                # Update the playlist
                user_item[field_to_edit] = update_user_playlist(user_item[field_to_edit], new_value)
            else:
                user_item[field_to_edit] = new_value
            
            # Upsert the updated item
            container.upsert_item(user_item)
            print(f"User '{user_id}' updated successfully.")
            print(f"Updated Document: {user_item}")
            return user_item[field_to_edit]
        else:
            print(f"Field '{field_to_edit}' not found in user '{user_id}'.")
            return -1  # Error code indicating failure
        
    else:
        print(f"User '{user_id}' not found.")
        return -1  # Error code indicating failure


def check_if_user_exist(user_id):
    query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
    try:
        items = container.query_items(query=query, enable_cross_partition_query=True)
        
        for item in items:
            # Extract relevant data from the item
            existing_user = {
                'id': item['id'],
                'user_id': item['user_id'],                
                'user_name': item['user_name'],
                'partition_key': item['partition_key'],
                'context_counter': item['context_counter'],
                'pfp': item['pfp'],
                'playlist': item['playlist']
            }

            # User already exists, retrieve context_counter and create an object
            return edit_user(existing_user['user_id'], existing_user['context_counter'], existing_user['context_counter'] + 1)
        
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
        query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))

        # Check if the item exists
        if items:
            item = items[0]
            item_id = item.get('id')

            if item_id:
                # Delete the item
                container.delete_item(item=item_id, partition_key=user_id)
                print(f"User '{user_id}' deleted successfully.")

            else:
                print(f"Error: 'id' field not found in the item.")

        else:
            print(f"User '{user_id}' not found.")

    except Exception as e:
        print(f"Error deleting user '{user_id}': {e}")


def print_all_user_ids_and_user_names():
    query = "SELECT c.user_id, c.partition_key, c.user_name FROM c"
    items = container.query_items(query=query, enable_cross_partition_query=True)

    for item in items:
        user_id = item.get('user_id', 'N/A')
        user_name = item.get('user_name', 'N/A')
        partition_key = item.get('partition_key', 'N/A')
        print(f"User ID: {user_id}, Username: {user_name}, Partition Key: {partition_key}")


def print_user_details_by_user_id(user_id):
    try:
        query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        if items:
            item = items[0]
            if 'user_id' in item:
                for item in items:        
                    for field, value in item.items():
                        print(f"{field.capitalize()}: {value}")            
            else:
                print(f"User '{user_id}' not found.")   

    except Exception as e:
        print(f"Error finding user '{user_id}': {e}")


# new_user=create_user('','', '', '', '')
# create_new_item(new_user)
# delete_user('')
# print_all_user_ids_and_user_names()
# print_user_details_by_user_id('')
# edit_user('', '', '')

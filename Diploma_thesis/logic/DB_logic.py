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
    """Generate a unique ID"""
    return str(uuid.uuid4())


def create_user(unique_id, email, user_name, pfp, playlist):
    """Create the structure for a user's account in the DB"""
    user_document = {
        'id': unique_id,  # unique id (internal need)
        'user_id': email,  # unique id (external need)
        'user_name': user_name,  # name to be displayed
        # '_rid': '',  uniquely identify the document
        # '_self': f'',  link to acces itself
        # '_etag': '',  optimistic concurrency control
        # '_attachments':  'attachments/',
        'partition_key': unique_id,
        # '_ts': ,  Timestamp
        'temporary_data': None,  
        'pfp': pfp,
        'playlist': playlist,
        'context': None
    }
    return user_document


fobbiden_fields = {
    'id', '_rid', '_self', '_etag', 'partition_key', '_ts'
}


def update_user_context(old_context, new_context):
    """Appends the new context to the old context, ensuring each context is a nested list."""
    # Check if old_context is a flat list and wrap it in a list if necessary
    if isinstance(old_context, list) and not isinstance(old_context[0], list):
        old_context = [old_context]
    
    # Append the new_context as a nested list
    updated_context = old_context + [new_context] if old_context else [new_context]
    return updated_context


def edit_user(user_id, field_to_edit, new_value):
    """Gets the field a user wants to edit and overrides it the new given data"""
    if field_to_edit in fobbiden_fields:
        print(f"Field '{field_to_edit}' is not editable.")
        return -1

    # Gets the item for that user
    query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    
    if items:
        # Assuming there's only one item with the given user_id
        user_item = items[0]

        # Check if the field exists in the user item
        if field_to_edit in user_item:
            # Update the existing field
            if field_to_edit == 'context':
                # Update the field for AI playlists with the new playlist
                user_item[field_to_edit] = update_user_context(user_item[field_to_edit], new_value)
            else:
                user_item[field_to_edit] = new_value

            # Upsert the updated item
            container.upsert_item(user_item)
            return True
        else:
            print(f"Field '{field_to_edit}' not found in user '{user_id}'.")
            return -1
    else:
        print(f"User '{user_id}' not found.")
        return -1


def check_if_user_exist(user_id):
    """Queries through all the items in the DB and success if a user is found"""
    query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
    try:
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        # If any items are returned, the user exists
        if items:
            return True
        else:
            return False
        
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error while querying Cosmos DB: {e}")
        return False


def create_new_item(item):
    """Creates a new item in the DB"""
    try:
        container.create_item(body=item)
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error while creating item in Cosmos DB: {e}")


def delete_user(user_id):
    """Completely deletes a user from the DB"""
    try:
        # Query for the item to be deleted
        query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))

        # Check if the item exists
        if items:
            item = items[0]
            item_id = item.get('id')

            if item_id:
                # Delete the epic games

                container.delete_item(item=item_id, partition_key=user_id)

            else:
                print(f"Error: 'id' field not found in the item.")

        else:
            print(f"User '{user_id}' not found.")

    except Exception as e:
        print(f"Error deleting user '{user_id}': {e}")


def print_all_user_ids_and_user_names():
    """The query returns every partition key and username in the DB"""
    query = "SELECT c.user_id, c.partition_key, c.user_name FROM c"
    items = container.query_items(query=query, enable_cross_partition_query=True)

    for item in items:
        user_id = item.get('user_id', 'N/A')
        user_name = item.get('user_name', 'N/A')
        partition_key = item.get('partition_key', 'N/A')
        print(f"User ID: {user_id}, Username: {user_name}, Partition Key: {partition_key}")


def print_user_details_by_user_id(user_id):
    """The query returns every detail for a user by searching with their username"""
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


def get_user_info(user_id, info_type):
    """Returns the specific filed for a user, requested by the arguments"""
    try:
        query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        if items:
            item = items[0]
            if 'user_id' in item:
                info = item.get(info_type, 'N/A')
                return info
            else:
                print(f"User '{user_id}' not found.")   

    except Exception as e:
        print(f"Error finding user '{user_id}': {e}")

# Example usages
# new_user=create_user('', '', '', '', '')
# create_new_item(new_user)
# delete_user('')
# print_all_user_ids_and_user_names()
# print_user_details_by_user_id('')
# get_user_playlist('')
# edit_user('', '', '')
# get_user_info('', '')
# check_if_user_exist('')

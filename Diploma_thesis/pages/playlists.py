from Diploma_thesis.templates import template
import reflex as rx
import json
from Diploma_thesis.logic.state import State


class PlaylistsState(rx.State):
    """Local instance of the rx.State class, which will be listening for events on this page"""
    should_init_dropdown: bool = False
    file_items_list: list = []

    def init_dropdown(self):
        self.should_init_dropdown = True
        self.file_items_list = find_playlists()

    def handle_selection(self, selected_option):
        """This method will be triggered when a selection is made.
        It sets the 'selected_playlist_id' state variable to the ID of the selected playlist,
        then writes the selected playlist's ID to temp.txt """
        try:
            # Get the ID from data formated: 'Name - ID'
            selected_play_list_id = selected_option.split(' - ')[1]

            with open('temp.txt', 'w') as file:
                json.dump(selected_play_list_id, file)

        except Exception as e:
            print(f"An error occurred while saving to 'temp.txt': {e}")
            return []

        # Redirect to '/new_playlist'
        return rx.redirect('/new_playlist')


def find_playlists():
    """Reads the temporary file then depending on the type of data in it:
    Returns the found information into a list or formats the data and returns it into a list"""
    try:
        # Open the temporary text file and read the content
        with open('temp.txt', 'r') as file:
            # Load the content from the file
            playlists_data = file.read().strip()

            # Check if the content is a JSON string
            try:
                playlists_data = json.loads(playlists_data)
            except json.JSONDecodeError:
                print("Invalid JSON in 'temp.txt'.")
                return []

            # Check if playlists_data is a list of dictionaries
            if isinstance(playlists_data, list) and all(isinstance(item, dict) for item in playlists_data):
                # Format every playlist in the data into 'Name - ID'
                formatted_list = [f"{playlist['name']} - {playlist['id']}" for playlist in playlists_data]
                return formatted_list
            elif isinstance(playlists_data, str):
                # Handle the case where the content is a single string
                return [playlists_data]
            else:
                print("Content in 'temp.txt' is not a list of dictionaries or a single string.")
                return []

    except FileNotFoundError:
        # Handle the case where the file does not exist
        print("File 'temp.txt' not found.")
        return []


def dropdown_menu():
    """Creates a dropdown menu when trigger is met"""
    dropdown_widget = rx.menu.root(
        rx.menu.trigger(
            rx.button("Select a playlist"),
        ),
        rx.menu.content(
            rx.foreach(  # Makes every item clickable
                PlaylistsState.file_items_list,
                lambda item: rx.menu.item(
                    item,
                    on_click=lambda option=item: PlaylistsState.handle_selection(option)
                )
            )
        )
    )
    empty_widget = None

    # Until the state isn't changed to be True (by pressing a button), nothing will be displayed
    return rx.cond(
        PlaylistsState.should_init_dropdown,
        dropdown_widget,
        empty_widget
    )


def init_button():
    """Returns the button that if pressed initializes the dropdown menu"""
    return rx.button("Initialize Dropdown", on_click=PlaylistsState.init_dropdown)


def previous_conversations_button():
    """Returns the button that if pressed redirects to /previous_conversations and loads the correct data"""
    return rx.button("Previous Conversations", on_click=State.get_user_previous_conversations)


@template(route="/playlists", title="Playlists Selection", image="/mlqko.jpg")
def playlists():
    """Creates the Playlists Selection page"""
    return rx.hstack(init_button(), dropdown_menu(), previous_conversations_button())

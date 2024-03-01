from Diploma_thesis.templates import template
import reflex as rx
import json
from Diploma_thesis.logic.state import State
from typing import List


class DropState(rx.State):
    """Local instance of the rx.State class, which will be listening for events on this page"""
    should_init_dropdown: bool = False
    file_items_list: List[List[str]] = []

    def init_dropdown(self):
        self.should_init_dropdown = True
        self.file_items_list = get_items_list()


def get_items_list():
    """Reads the temporary file then returns the found information into a list of lists"""
    try:
        # Open the temporary text file and read the content
        with open('temp.txt', 'r') as file:
            # Load the content from the file
            playlists_data = file.read().strip()

            # Check if the content is a JSON string
            try:
                playlists_data = json.loads(playlists_data)
                return [playlists_data]
            
            except json.JSONDecodeError:
                print("Invalid JSON in 'temp.txt'.")
                return []          

    except FileNotFoundError:
        # Handle the case where the file does not exist
        print("File 'temp.txt' not found.")
        return []


def accordion():
    """Creates a dropdown menu of type accordion when trigger is met"""
    return rx.chakra.accordion(
        rx.foreach(
            DropState.file_items_list,
            lambda item_list: rx.chakra.accordion_item(
                rx.foreach(
                    item_list,
                    lambda item: rx.chakra.box(item)
                )
            )
        )
    )


def init_button():
    """Returns the button that if pressed initializes the dropdown menu"""
    return rx.button("Show previous recommendtions", on_click=DropState.init_dropdown)


def create_dropdown_conditional():
    """ Returns a  condition in which until the state isn't changed to be True, nothing will be displayed"""
    return rx.cond(
        DropState.should_init_dropdown,
        accordion(),  
        None
    )


def back_to_playlist_button():
    """Returns the button that if pressed redirects to /playlists and loads the correct data"""
    return rx.button("Back to playlist", on_click=State.correct_behaviour_sequence('/playlists'))


@template(route="/previous_conversations", title="Previous Conversations", image="/mlqko.jpg")
def previous_conversations():
    """Creates the Previous Conversations page"""
    return rx.vstack(       
        init_button(),   
        create_dropdown_conditional(),
        back_to_playlist_button(),
    )

from Diploma_thesis.templates import template
import reflex as rx
import json
from Diploma_thesis.logic.state import State


class DropState(rx.State):
    should_init_dropdown: bool = False
    file_items_list: list = []

    def init_dropdown(self):
        self.should_init_dropdown = True
        self.file_items_list = get_items_list()


def get_items_list():
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
    return rx.chakra.accordion(
        rx.foreach(
            DropState.file_items_list,
            lambda item: rx.chakra.accordion_item(
                item
            )
        )
    )
       

def init_button():
    return rx.button("Init", on_click=DropState.init_dropdown)


def create_dropdown_conditional():
    return rx.cond(
        DropState.should_init_dropdown,
        accordion(),  
        None
    )


def back_to_playlist_button():
    return rx.button("Back to playlist", on_click=State.function_train('/playlists'))


@template(route="/previous_conversations", title="Previous Conversations", image="/mlqko.jpg")
def previous_conversations():
    return rx.container(
        rx.vstack(
            init_button(),   
            create_dropdown_conditional(),
            back_to_playlist_button(),
        )
    )

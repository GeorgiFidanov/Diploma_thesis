from Diploma_thesis.templates import template
import reflex as rx
from Diploma_thesis.logic.state import State


class ButtonState(rx.State):
    """Local instance of the rx.State class, which will be listening for events on this page"""
    playlist_name: str = ''
    playlist_details: str = ''

    def clear_text(self):
        self.playlist_name = ''
        self.playlist_details = ''


def form():
    """Creates a form that automatically sets the user input as values for 'playlist_name' and 'playlist_details'.
    When user desides to submit it, the logic for creating a new playlist is activated."""
    return rx.chakra.vstack(
        rx.chakra.input(
            placeholder="Name for new playlist",
            value=ButtonState.playlist_name,
            on_change=ButtonState.set_playlist_name,
        ),
        rx.chakra.input(
            placeholder="(Optional) bonus details for the playlist",
            value=ButtonState.playlist_details,
            on_change=ButtonState.set_playlist_details
        ),
        rx.chakra.hstack(
            rx.chakra.button(
                "Clear",
                on_click=ButtonState.clear_text
            ),

            rx.chakra.button(
                "Submit",
                on_click=State.create_new_playlist(ButtonState.playlist_name, ButtonState.playlist_details)
            )
        ),       
    )


@template(route="/new_playlist", title="New playlist", image="/mlqko.jpg")
def new_playlist():
    """Creates the New playlist page"""
    return rx.vstack(
        form()       
    )

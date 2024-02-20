from Diploma_thesis.templates import template
import reflex as rx
from Diploma_thesis.logic.state import State


class ButtonState(rx.State):
    playlist_name: str = ''
    playlist_details: str = ''

    def clear_text(self):
        self.playlist_name = ''
        self.playlist_details = ''

def form():
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
            rx.chakra.button("Clear", on_click=ButtonState.clear_text),

            rx.chakra.button("Submit", on_click=State.create_new_playlist(ButtonState.playlist_name, ButtonState.playlist_details))
        ),       
    )


@template(route="/new_playlist", title="New playlist", image="/mlqko.jpg")
def new_playlist():
    return rx.vstack(
        form()       
    )

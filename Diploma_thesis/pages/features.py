from Diploma_thesis.templates import template
import reflex as rx
from Diploma_thesis.logic.state import State


@template(route="/features", title="Features", image="/mlqko.jpg", on_load=State.correct_behaviour_sequence(''))
def features() -> rx.Component:
    """Creates the features page"""
    return rx.vstack(
        rx.stack(
            rx.button(
                "Playlists",
                on_click=rx.redirect('/playlists') 
                ),
            rx.button(
                "Concerts",
                on_click=rx.redirect('/location_search') 
                ),
            direction="row"
        ),
        rx.spacer(),
        # Until the app isn't authenticated the buttons will appear grey
        opacity=rx.cond(State.app_is_authenticated, 1, 0.3),
        height='100%',
    )

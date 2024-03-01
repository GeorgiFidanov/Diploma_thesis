from Diploma_thesis.templates import template
import reflex as rx
from Diploma_thesis.logic.state import State
from Diploma_thesis.logic.misc import clear_temp_file


def authenticate_alert() -> rx.Component:
    """Creates an alert that the app still isn't authenticated"""
    return rx.chakra.alert(
        rx.chakra.alert_icon(),
        rx.chakra.alert_title('Log in Spotify to use the website', width='100%'),
        rx.chakra.alert_description(
            rx.hstack(
                rx.spacer(),
                rx.button(
                    'Log in',
                    on_click=rx.redirect(
                        # Redirect to the app authentication URL
                        State.spotify_auth_url,
                        external=False
                    )
                )
            ),
            width='100%'
        ),
        status='error',
        border_radius='lg',
        z_index=2
    )


@template(route="/", title="Home", image="/mlqko.jpg", on_load=State.on_page_load())
def index() -> rx.Component:
    """Creates the index page"""
    clear_temp_file()  # Clean/Create the temp file to ensure correct behaviour
    return rx.container(
        rx.vstack(
            rx.box(
                rx.cond(
                    State.app_is_authenticated,  # This is the condition
                    rx.box(
                        rx.button(
                            "To app",
                            on_click=State.correct_behaviour_sequence('/features')
                            )  # Returns this box if the condition is mrt
                    ),
                    authenticate_alert()  # Returns this alert if the condition isn't met
                ),
                width='60vw',
                height='0vh'
            ),
            height='100vh',             	
        )
    )

from Diploma_thesis import styles
from typing import Callable, Union, List

import reflex as rx

# Meta tags for the app.
default_meta = [
    {
        "name": "viewport",
        "content": "width=device-width, shrink-to-fit=no, initial-scale=1",
    },
]

def light_button() -> rx.Component:
    """A light switch button."""
    return rx.chakra.color_mode_button(
        rx.chakra.color_mode_icon(),
        color_scheme="none",
        _dark={"color": "white"},
        _light={"color": "black"},
    )

def menu_button() -> rx.Component:
    from reflex.page import get_decorated_pages

    return rx.box(
        rx.chakra.menu(
            rx.chakra.menu_button(
                rx.chakra.icon(tag="hamburger")
            ),
            rx.chakra.menu_list(
                *[
                    rx.chakra.menu_item(
                        rx.link(
                            page["title"],
                            href=page["route"],
                            width="100%",
                        )
                    )
                    for page in get_decorated_pages()
                ],
                rx.chakra.menu_divider(),
                rx.chakra.menu_item(
                    rx.link("About", href="https://github.com/GeorgiFidanov", width="100%")
                ),
                rx.chakra.menu_item(
                    rx.link("Contact", href="mailto:georgi.fidanov05@gmail.com", width="100%")
                ),
            ),
        ),
    )

def template(
    route: Union[str, None] = None,
    title: Union[str, None] = None,
    image: Union[str, None] = None,
    description: Union[str, None] = None,
    meta: Union[str, None] = None,
    script_tags: Union[List[rx.Component], None] = None,
    on_load: Union[rx.event.EventHandler, List[rx.event.EventHandler], None] = None,
) -> Callable[[Callable[[], rx.Component]], rx.Component]:
    # Function body remains the same
    def decorator(page_content: Callable[[], rx.Component]) -> rx.Component:
        all_meta = [*default_meta, *(meta or [])]

        @rx.page(
            route=route,
            title=title,
            image=image,
            description=description,
            meta=all_meta,
            script_tags=script_tags,
            on_load=on_load,
        )
        def templated_page():
            return rx.hstack(
                rx.box(
                    rx.box(
                        rx.hstack(
                            menu_button(),
                            light_button(),  # Place the light button next to the menu button
                            align_items="center",  # Align items in the header
                            justify_content="space-between",  # Space between menu and light switch
                            padding="1em",  # Add some padding around the header
                        ),
                        position="fixed",
                        right="1.5em",
                        top="1.5em",
                        z_index="500",
                    ),
                    rx.box(
                        page_content(),
                        **styles.template_content_style,
                        margin="auto",  # Center the content
                        width="80%",  # Adjust the width as needed
                    ),
                    **styles.template_page_style,
                ),
                align_items="flex-start",
                transition="left   0.5s, width   0.5s",
                position="relative",
            )

        return templated_page

    return decorator
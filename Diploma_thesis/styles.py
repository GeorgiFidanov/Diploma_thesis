"""Styles for the app."""
# For now default values are used, to be changed in future updates
import reflex as rx

border_radius = "0.375rem"
box_shadow = "0px 0px 0px 1px rgba(84, 82, 95, 0.14)"
border = "1px solid #F4F3F6"
text_color = "black"
accent_text_color = "#1A1060"
accent_color = "#F5EFFE"
hover_accent_color = {"_hover": {"color": accent_color}}
hover_accent_bg = {"_hover": {"bg": accent_color}}
content_width_vw = "90vw"
sidebar_width = "20em"

template_page_style = {"padding_top": "5em", "padding_x": ["auto", "2em"], "flex": "1"}

template_content_style = {
    "align_items": "flex-start",
    "box_shadow": box_shadow,
    "border_radius": border_radius,
    "padding": "1em",
    "margin_bottom": "2em",
}

link_style = {
    "color": text_color,
    "text_decoration": "none",
    **hover_accent_color,
}

overlapping_button_style = {
    "background_color": "white",
    "border": border,
    "border_radius": border_radius,
}

""" Styles valid until 0.4.0 - 18.02.2024
base_style = {
    rx.MenuButton: {
        "width": "3em",
        "height": "3em",
        **overlapping_button_style,
    },
    rx.MenuItem: hover_accent_bg,
}
"""


markdown_style = {
    "code": lambda text: rx.code(text, color="#1F1944", bg="#EAE4FD"),
    "a": lambda text, **props: rx.link(
        text,
        **props,
        font_weight="bold",
        color="#03030B",
        text_decoration="underline",
        text_decoration_color="#AD9BF8",
        _hover={
            "color": "#AD9BF8",
            "text_decoration": "underline",
            "text_decoration_color": "#03030B",
        },
    ),
}


component_styles = {

    rx.text: {
        "font-family": "Arial, sans-serif",
        "color": "black",
    },

    rx.heading: {
        "font-weight": "bold",
        "color": "black",
    },

     rx.box: {
        "padding": "2em",  # Increase padding to create more space around the content
        "margin": "0 auto",  # Center the box horizontally
        "max-width": "90vw",  # Limit the maximum width to make the website feel wider
        "border-radius": "1rem",
        "border": "1px solid black",
        "box-shadow": "0  0  10px  0 rgba(0,  0,  0,  0.2)",
        "display": "flex",  # Use flexbox to center content
        "flex-direction": "column",  # Stack children vertically
        "align-items": "center",  # Center children horizontally
        "justify-content": "center",  # Center children vertically
    },
    
    rx.box: {
        "padding": "0",
        "margin": "0",
        "border-radius": "1rem",
        "border": "1px solid black",
        "box-shadow": "0 0 10px 0 rgba(0, 0, 0, 0.2)",
    },

    rx.hstack: {
        "padding": "2em",  # Increase padding to create more space around the content
        "margin": "0 auto",  # Center the box horizontally
        "max-width": "90vw",  # Limit the maximum width to make the website feel wider
        "border-radius": "1rem",
        "border": "1px solid black",
        "box-shadow": "0  0  10px  0 rgba(0,  0,  0,  0.2)",
        "display": "flex",  # Use flexbox to center content
        "flex-direction": "column",  # Stack children vertically
        "align-items": "center",  # Center children horizontally
        "justify-content": "center",  # Center children vertically
    },

    # Specific styles for vertical stacks
    rx.vstack: {
        "flex-direction": "column",  # Stack children vertically
        "align-items": "center",  # Center children horizontally
        "justify-content": "center",  # Center children vertically
        "gap": "1em",  # Add space between items in the stack
    },

}
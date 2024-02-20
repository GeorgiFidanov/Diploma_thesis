"""Main App"""

from Diploma_thesis import styles
import reflex as rx
from Diploma_thesis.pages import *

# Create the app.
app = rx.App(component_styles=styles.component_styles)
app.add_page(index)
app.add_page(features)
app.add_page(playlists)
app.add_page(location_search)
app.add_page(new_playlist)
app.add_page(previous_conversations)

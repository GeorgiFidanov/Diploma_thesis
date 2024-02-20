from Diploma_thesis.logic.location_api import *
from Diploma_thesis.templates import template
import reflex as rx


class LocationSearchState(rx.State):
    """Local instance of the rx.State class, which will be listening for events on this page"""
    city: str = ''
    artist_name: str = ''
    search_result: str = ''

    def update_city(self, value):
        """Sets the new given value for the city string"""
        self.city = value

    def update_artist_name(self, value):
        """Sets the new given value for the artist name string"""
        self.artist_name = value

    def perform_search(self):
        """Calls the logic from the location_api to search for events.
        First verifies that the city exists.
        Then if the 'artist_name' is empty returns all avaible artists in that city.
        Otherwise, continues the search normally.
        The result of the search is stored in the 'search_result' string"""

        response = get_location_api_responce(self.city)

        if 'data' in response:
            if self.artist_name:
                result = find_artist_location(response, self.artist_name)
                if result:
                    self.search_result = f"Address Locality: {result['addressLocality']}\nStreet Address: \
                                                            {result['streetAddress']}"
                else:
                    self.search_result = "Artist not found."
            else:
                artists = "Artists: "
                for event in response['data']:
                    for performer in event['performer']:
                        artists += performer['name'] + ', '

                self.search_result = artists
        else:
            self.search_result = "City not found."


@template(route="/location_search", title="Location search", image="/mlqko.jpg")
def location_search():
    """Creates the location search page"""
    return rx.vstack(
        rx.vstack(
            rx.chakra.Input(
                placeholder="City",
                on_change=LocationSearchState.update_city
            ),
            rx.chakra.Input(
                placeholder="Artist Name",
                on_change=LocationSearchState.update_artist_name
            ),
            rx.button(
                "Search",
                on_click=LocationSearchState.perform_search,
            ),
            rx.text("If field artist is empty, the search will \
                return all avaible artists in the city.")
        ),
        rx.text(LocationSearchState.search_result)  # By default, it doesn't display anything
    )

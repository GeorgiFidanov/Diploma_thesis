from dotenv import load_dotenv
import os
from urllib.parse import urlencode
import json
import reflex as rx
import random
import string
import base64
import time
from spotipy import Spotify
from requests import post, get
from Diploma_thesis.logic.DB_logic import \
    check_if_user_exist, create_new_item, create_user, generate_uuid, edit_user, get_user_info
from Diploma_thesis.logic.AI_part import generate_recommendations
from Diploma_thesis.logic.misc import clean_song_list
from typing import List, Dict, Optional


load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


REDIRECT_URI = 'http://localhost:1234/'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'


def remove_duplicate_playlists(playlists):
    """Removes any duplicate playlists"""
    seen_playlists = set()
    unique_playlists = []
    for playlist in playlists:
        playlist_name = playlist['name']
        if playlist_name not in seen_playlists:
            unique_playlists.append(playlist)
            seen_playlists.add(playlist_name)
    return unique_playlists


def token_expired(token_dict) -> None:
    """Check if token has expired"""
    # Check if self.tokens is a string and try to parse it as JSON
    if isinstance(token_dict, str):
        try:
            tokens_dict = json.loads(token_dict)
        except json.JSONDecodeError:
            print("Error: self.tokens is not a valid JSON string.")
            return
    elif isinstance(token_dict, dict):
        tokens_dict = token_dict
    else:
        print("Error: self.tokens is neither a string nor a dictionary.")
        return
    return tokens_dict['expires_at'] <= time.time()


class State(rx.State):
    """The app's base state - contains logic around authentication, track data, and user data."""

    @rx.var
    def callback_code_and_state(self) -> tuple[Optional[str], Optional[str]]:
        """Code and state from callback uri after redirect"""
        args = self.router.page.params
        code = args.get('code', None)
        state = args.get('state', None)
        return code, state

    # Add random characters at the end to ensure Auth2
    state_code: str = ''.join(
        random.choice(
            string.ascii_letters + string.digits
        )
    )

    @rx.var
    def spotify_auth_url(self) -> str:
        """Url to Spotify authentication page"""

        permissions = 'user-library-read user-read-private user-read-email playlist-modify-private\
            playlist-read-private user-library-modify playlist-read-collaborative playlist-modify-public'

        params = {
            'response_type': 'code',
            'client_id': client_id,
            'scope': permissions,
            'redirect_uri': REDIRECT_URI,
            'state': self.state_code,
            'show_dialog': True
        }

        auth_url = f"{AUTH_URL}?{urlencode(params)}"
        return auth_url

    tokens: str = rx.Cookie("", name='spotify_tokens')
    user_id: str = rx.LocalStorage("", name='user_id')  # Used in the fields related with DB usage
    user_spotify_id: str = rx.LocalStorage("", name='user_spotify_id')  # Used in requests with the Spotify's api
    
    def get_specific_token(self, token):
        """Returns only the authentication token from the cookie"""
        if not self.tokens:
            print("Authentication token not found.")            
            return

        # Check if self.tokens is a string and try to parse it as JSON
        if isinstance(self.tokens, str):
            try:
                tokens_dict = json.loads(self.tokens)
            except json.JSONDecodeError:
                print("Error: self.tokens is not a valid JSON string.")
                return
        elif isinstance(self.tokens, dict):
            tokens_dict = self.tokens
        else:
            print("Error: self.tokens is neither a string nor a dictionary.")
            return

        # Now .get() can be used on the dictionary
        specific_token = tokens_dict.get(token)
        return specific_token

    def add_token_expiry_time(self, token_dict: dict) -> dict:
        """Updates a tokens with an expiration timestamp derived from the expires_in value,
         or sets a default expiration time if expires_in is not provided."""
        expires_in = token_dict.get('expires_in')
        if expires_in is not None:
            # Convert expires_in to an integer and add it to the current time
            token_dict['expires_at'] = int(time.time()) + int(expires_in)
        else:
            token_dict['expires_at'] = int(time.time()) + 3600  # Default to  1 hour from now

        return token_dict

    def get_tokens_from_callback(self):
        """Request an authentication token from Spotify based on the code
        provided in the redirect. If the state string provided in tbe redirect
        does not match that provided for the authentication url, it doesn't get accepted.
        Also updates state var with provided tokens"""
                
        code, state = self.callback_code_and_state
        if state == self.state_code:  # confirming that the request state and response state match

            auth_options = {
                'url': TOKEN_URL,
                'data': {
                    'code': code,
                    'redirect_uri': REDIRECT_URI,
                    'grant_type': 'authorization_code'
                },
                'headers': {
                    'content-type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Basic ' + base64.b64encode(
                            (client_id + ':' + client_secret).encode()
                        ).decode('utf-8')
                }
            }

            response = post(
                auth_options['url'],
                data=auth_options['data'],
                headers=auth_options['headers']
            )

            enriched_response_dict = self.add_token_expiry_time(response.json())
            self.tokens = json.dumps(enriched_response_dict) 
        else:
            print("Error with get_tokens_from_callback(): states mismatch")

    def refresh_auth_token(self):
        """Use authentication token's 'refresh_token' property to request a new
        spotify authenticatioun token. Also updates the state var accordingly"""

        refresh_token = self.get_specific_token('refresh_token')

        auth_options = {
            'url': TOKEN_URL,
            'data': {
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            },
            'headers': {
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + base64.b64encode(
                    (client_id + ':' + client_secret).encode()
                                            ).decode('utf-8')  
            }
        }

        response = post(
            auth_options['url'],
            data=auth_options['data'],
            headers=auth_options['headers']
        )
        # Add comments here
        enriched_response_dict = {
            **self.add_token_expiry_time(response.json()),
            'refresh_token': refresh_token
        }
        self.tokens = json.dumps(enriched_response_dict)

    @rx.var
    def app_is_authenticated(self) -> bool:
        """Returns true if there are tokens"""
        return len(self.tokens) > 0

    def get_Spotify_instance(self) -> Spotify:
        """Gets a spotify instance"""
        if self.app_is_authenticated:
            access_token = self.get_specific_token('access_token')
            return Spotify(auth=access_token)
        
        # Redirect to the app authentication URL
        return rx.redirect(State.spotify_auth_url, external=False)

    def on_page_load(self):
        """When the index page is first loaded, makes the connection to Spotify authentication page
        or refreshes the tokens"""

        if not self.app_is_authenticated:
            if self.callback_code_and_state != (None, None):
                self.get_tokens_from_callback()
        else:
            if token_expired(self.tokens):  
                self.refresh_auth_token()

    def create_playlist(self, playlist_name, songs):
        """"Creates a playlist in the user's Spotify library"""
        if token_expired(self.tokens):  
            self.refresh_auth_token()
        spotify_instance = self.get_Spotify_instance()
        playlist = spotify_instance.user_playlist_create(user=self.user_spotify_id, name=playlist_name, public=False)
        playlist_id = playlist['id']

        if playlist_id:
            for song in songs:
                artist_name = song['artist_name']
                track_name = song['track_name']
                query = f'track:{track_name} artist:{artist_name}'
                results = spotify_instance.search(query, type='track', limit=1)

                # Check if the track was found
                if results['tracks']['total'] > 0:
                    track = results['tracks']['items'][0]
                    track_uri = track['uri']
                    spotify_instance.playlist_add_items(playlist_id, [track_uri])
                else:
                    print(f"Track '{track_name}' by '{artist_name}' not found.")

            return playlist_id

    all_playlists = []

    def fetch_all_user_playlists(self):
        """Gets all user's playlists"""

        spotify_instance = self.get_Spotify_instance()
        self.user_spotify_id = spotify_instance.current_user()['id']
        playlists = spotify_instance.user_playlists(self.user_spotify_id)
        playlist = playlists['items']
        while playlists['next']:
            playlists = self.get_Spotify_instance().next(playlists)
            playlist.extend(playlists['items'])
        self.all_playlists.extend(playlist)

    def save_playlists_data(self, data: List[Dict[str, str]]) -> None:
        """Saves the playlists data to a temporary text file."""
        try:
            # Open the temporary text file and write the JSON data
            with open('temp.txt', 'w') as file:
                json.dump(data, file)

        except Exception as e:
            # Handle any exceptions that occur during file writing
            print(f"An error occurred while saving to 'temp.txt': {e}")
            return None
        
    def filter_playlists_by_id_and_name(self):
        """Extracts only the ids and names for each playlist"""
        self.all_playlists = remove_duplicate_playlists(self.all_playlists)
        filtered_playlists = [{'id': playlist['id'], 'name': playlist['name']} for playlist in self.all_playlists]
        return filtered_playlists

    def get_playlist_tracks(self, spotify_playlist_id):
        """Gets all songs name from playlist"""

        if token_expired(self.tokens):  
            self.refresh_auth_token()

        access_token = self.get_specific_token('access_token')
        response = get(API_BASE_URL + f'playlists/{spotify_playlist_id}/tracks',
                       headers={'Authorization': f"Bearer {access_token}"})

        if response.status_code == 200:
            playlist_tracks = response.json()
            return playlist_tracks
        else:
            # Raises an exception when the API call fails
            raise RuntimeError(f"Unable to fetch playlist tracks: {response.content}")

    def get_audio_features_from_track_id(self, track_id):
        """Gets specific audio features from a song"""

        if token_expired(self.tokens):  
            self.refresh_auth_token()

        access_token = self.get_specific_token('access_token')
        response = get(API_BASE_URL + f'audio-features/{track_id}',
                       headers={'Authorization': f"Bearer {access_token}"})

        audio_features = response.json()
        # Filter out only the needed audio features
        filtered_audio_features = {
            "acousticness": audio_features['acousticness'],
            "danceability": audio_features['danceability'],
            "energy": audio_features['energy'],
            "instrumentalness": audio_features['instrumentalness'],
            # This is the key the track is in. Integers map to pitches using standard Pitch Class notation.
            "key": audio_features['key'],
            "liveness": audio_features['liveness'],
            "loudness": audio_features['loudness'],
            "speechiness": audio_features['speechiness'],
            "tempo": audio_features['tempo'],
            "valence": audio_features['valence']
        }
        return filtered_audio_features

    def extract_song_info(self, song_data):
        """Gets only needed the features from a song"""
        audio_info = self.get_audio_features_from_track_id(song_data['track']['id'])
        song_info = {
            "name": song_data['track']['name'],
            "album_name": song_data['track']['album']['name'],
            "artist_name": song_data['track']['artists'][0]['name'],
            "external_url": song_data['track']['external_urls']['spotify'],
            "acousticness": audio_info['acousticness'],
            "danceability": audio_info['danceability'],
            "energy": audio_info['energy'],
            "instrumentalness": audio_info['instrumentalness'],
            "key": audio_info['key'],
            "liveness": audio_info['liveness'],
            "loudness": audio_info['loudness'],
            "speechiness": audio_info['speechiness'],
            "tempo": audio_info['tempo'],
            "valence": audio_info['valence']
        }
        return song_info

    def clear_songs_data(self, playlist_id):
        """From a playlist, gathers all the songs
        then from each song extracts the needed details"""
        try:
            songs_data = self.get_playlist_tracks(playlist_id)
        except RuntimeError as e:
            print(f"Error fetching playlist tracks: {e}")
            return []  # Return an empty list

        filtered_songs = []
        for song in songs_data['items']:
            filtered_song_data = self.extract_song_info(song)
            filtered_songs.append(filtered_song_data)
        return filtered_songs

    def create_user_in_db(self):
        """Gets the user's Spotify account info and uses it to create a profile in DB"""
        access_token = self.get_specific_token('access_token')

        if not access_token:
            print("Access token not found in the authentication token.")
            return

        response = get(API_BASE_URL + 'me', headers={'Authorization': f"Bearer {access_token}"})
        user_profile = response.json()

        # Check if 'display_name' is present in the response
        if 'display_name' in user_profile and user_profile['display_name'] is not None:
            self.user_spotify_id = user_profile['id']

            username = user_profile['display_name']
            email = user_profile['email']
            profile_picture_url = user_profile['images'][0]['url'] if user_profile['images'] else None
            playlist_to_work_with = None

            if check_if_user_exist(email) is False:
                user_data = create_user(generate_uuid(), email, username, profile_picture_url, playlist_to_work_with)
                create_new_item(user_data)        
            
            self.user_id = email

        else:
            return RuntimeError({"error": "User info not found in the response."})

    def separate_name_and_tracks(self, song_list):
        """After AI's responce, extracts the playlist name from the responce"""
        # Check if the responce is not empty and has more than one element
        if song_list and len(song_list) > 1:
            # Slice the list to exclude the first element (playlist name)
            ai_playlist_name = song_list[0]
            song_list = song_list[1:]
            return ai_playlist_name, song_list
        else:
            return RuntimeError({"error": "Error separating name and tracks in AI's responce."})

    def create_new_playlist(self, playlist_name, bonus_details):
        """Generate the new AI playlist"""
        # Read from temp.txt

        with open('temp.txt', 'r') as file:
            # Load the JSON data from the file
            playlist_real_id = json.load(file)

        if playlist_real_id:

            playlist_to_work_with = self.clear_songs_data(playlist_real_id)
            edit_user(self.user_id, 'playlist', playlist_to_work_with)

            # Generate recommendations and store them in finale
            ai_playlist = generate_recommendations(self.user_id, playlist_to_work_with, playlist_name, bonus_details)
            song_name, song_list = self.separate_name_and_tracks(ai_playlist)
            
            clean_ai_songs = clean_song_list(song_list)

            new_playlist_id = self.create_playlist(song_name, clean_ai_songs)

            # Write the id of the new playlist to temp.txt, overwriting its previous contents
            with open('temp.txt', 'w') as file:
                json.dump(new_playlist_id, file)
                return None

        else:
            return RuntimeError({"error": "No playlist selected."})

    def correct_behaviour_sequence(self, where):
        """Sequence of functions needed to excecuted to ensure correct behaviour"""
        if not self.app_is_authenticated:
            return rx.redirect(self.spotify_auth_url, external=False) 
        if token_expired(self.tokens):  
            self.refresh_auth_token()
        self.fetch_all_user_playlists()
        clean_playlists = self.filter_playlists_by_id_and_name()
        self.save_playlists_data(clean_playlists)
        self.create_user_in_db()
        if where != '':
            return rx.redirect(where)

    def get_user_previous_conversations(self):
        """Sequence of functions needed to display all previous AI playlists"""
        self.save_playlists_data(get_user_info(self.user_id, 'context'))
        return rx.redirect('/previous_conversations')

from dotenv import load_dotenv
import os
from requests import post, get
from urllib.parse import urlencode
from flask import Flask, request, redirect, url_for, session, jsonify, render_template
from datetime import datetime
from loader import check_if_user_exist, create_new_item, create_user

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

REDIRECT_URI = 'http://localhost:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'
playlists_data = {}


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    session.clear()

    permissions = 'user-library-read user-read-private user-read-email playlist-read-private user-library-modify'

    params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': permissions,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True 
    }
    auth_url = f"{AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)


@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})

    if 'code' in request.args:
        response = post(TOKEN_URL, data={
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': client_id,
            'client_secret': client_secret
            }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        
        token_info = response.json()
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        return redirect(url_for('playlists'))


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect(url_for('login'))

    response = post(TOKEN_URL, data={
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token'],
        'client_id': client_id,
        'client_secret': client_secret
    })

    new_token_info = response.json()
    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

    return redirect(url_for('playlists'))


def fetch_all_user_playlists(access_token):
    all_playlists = []

    api_url = API_BASE_URL + 'me/playlists'
    while api_url:
        response = get(api_url, headers={'Authorization': f"Bearer {access_token}"})
        data = response.json()

        # Append the playlists from the current response
        all_playlists.extend(data.get('items', []))

        # Check if there are more playlists to fetch
        api_url = data.get('next')

    return all_playlists


@app.route('/playlists')
def playlists():
    global playlists_data

    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect(url_for('refresh-token'))

    all_playlists = fetch_all_user_playlists(session['access_token'])
    
    # Extract relevant information for each playlist
    filtered_playlists = [{'name': playlist['name'], 'id': playlist['id']} for playlist in all_playlists]
    playlists_data = filtered_playlists
    return render_template('playlists.html', filtered_playlists=filtered_playlists)


def get_playlist_tracks(playlist_id):
    response = get(API_BASE_URL + f'playlists/{playlist_id}/tracks',
                   headers={'Authorization': f"Bearer {session['access_token']}"})
    
    if response.status_code == 200:
        playlist_tracks = response.json()
        return playlist_tracks
    else:
        return jsonify({"error": "Unable to fetch playlist tracks"}), response.status_code


def extract_song_info(song_data):
    # Extracting relevant information
    song_info = {
        "name": song_data.get("name"),
        "album_name": song_data.get("album", {}).get("name"),
        "artist_name": song_data.get("artists", [{}])[0].get("name"),
        "danceability": song_data.get("danceability"),
        "energy": song_data.get("energy"),
        "key": song_data.get("key"),
        "tempo": song_data.get("tempo"),
        "external_url": song_data.get("external_urls", {}).get("spotify")
    }

    return song_info


def clear_songs_data(playlist_id):
    songs_data = get_playlist_tracks(playlist_id)
    filtered_songs = []
    for song in songs_data:
        filtered_song_data = extract_song_info(song)
        filtered_songs.append(filtered_song_data)
    return filtered_songs


def get_playlist_id_by_number(playlists_data, selected_number):
    for index, playlist in enumerate(playlists_data):
        if index + 1 == selected_number:
            # Match found, return the playlist id
            return playlist.get('id')

    # Return None if no match is found
    return None


@app.route('/user', methods=['POST'])
def user():
    selected_index = int(request.form.get('selected_index'))

    playlist_id = get_playlist_id_by_number(playlists_data, selected_index)

    if playlist_id:
        
        print(f"Selected Index: {selected_index}")
        print(f"Extracted Playlist ID: {playlist_id}")

        response = get(API_BASE_URL + 'me', headers={'Authorization': f"Bearer {session['access_token']}"})
        user_profile = response.json()

        # Check if 'display_name' is present in the response
        if 'display_name' in user_profile and user_profile['display_name'] is not None:
            username = user_profile['display_name']
            email = user_profile['email']
            profile_picture_url = user_profile['images'][0]['url'] if user_profile['images'] else None

            if check_if_user_exist(username) == 0:
                user_data = create_user(username, email, username, profile_picture_url, clear_songs_data(playlist_id))
                create_new_item(user_data)
                return jsonify({"message": "User created successfully."})
            else:
                raise RuntimeError("User already exists.")
        else:
            return jsonify({"error": "User info not found in the response."})
    else:
        print("No playlist selected.")
        return jsonify({"error": "No playlist selected."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
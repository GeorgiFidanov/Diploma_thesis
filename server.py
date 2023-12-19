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


@app.route('/playlists')
def playlists():
    global playlists_data  # Declare that you're using the global variable
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect(url_for('refresh-token'))

    playlists_response = get(API_BASE_URL + 'me/playlists',
                             headers={'Authorization': f"Bearer {session['access_token']}"})
    playlists_data = playlists_response.json()

    return render_template('playlists.html', playlists=playlists_data)


def get_playlist_tracks(playlist_id):
    response = get(API_BASE_URL + f'playlists/{playlist_id}/tracks',
                   headers={'Authorization': f"Bearer {session['access_token']}"})
    
    if response.status_code == 200:
        playlist_tracks = response.json()
        return playlist_tracks
    else:
        return jsonify({"error": "Unable to fetch playlist tracks"}), response.status_code


@app.route('/user', methods=['POST'])
def user():
    selected_index = int(request.form.get('selected_index'))

    global playlists_data
    if playlists_data and 'items' in playlists_data and 0 <= selected_index < len(playlists_data['items']):
        selected_playlist = playlists_data['items'][selected_index]
        playlist_id = selected_playlist['id']

        response = get(API_BASE_URL + 'me', headers={'Authorization': f"Bearer {session['access_token']}"})
        user_profile = response.json()

        # Check if 'display_name' is present in the response
        if 'display_name' in user_profile and user_profile['display_name'] is not None:
            username = user_profile['display_name']
            email = user_profile['email']
            profile_picture_url = user_profile['images'][0]['url'] if user_profile['images'] else None

            if check_if_user_exist(username) == 0:
                user_data = create_user(username, email, profile_picture_url, get_playlist_tracks(playlist_id))
                create_new_item(user_data)
                return jsonify({"message": "User created successfully."})
            else:
                raise RuntimeError("User already exists.")
        else:
            return jsonify({"error": "User info not found in the response."})
    else:
        return jsonify({"error": "No playlist selected."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

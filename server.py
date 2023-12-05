from dotenv import load_dotenv
import os
from requests import post, get
from urllib.parse import urlencode
from flask import Flask, request, redirect, url_for, session, jsonify
from datetime import datetime

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

REDIRECT_URI = 'http://localhost:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    session.clear()
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': 'user-library-read user-read-private user-read-email',
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
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect(url_for('/refresh-token'))
    
    response = get(API_BASE_URL + 'me/playlists',
            headers={'Authorization': f"Bearer {session['access_token']}"})
    playlists = response.json()
    # username = playlists['display_name']
    # email = playlists['email']
    # profile_picture_url = playlists['images'][0]['url'] if playlists['images'] else None

    return jsonify(playlists)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

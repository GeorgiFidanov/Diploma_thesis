import requests
from urllib.parse import urlencode
from flask import Flask, request, redirect, url_for, session, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = '34g23rgb2r2b-f-3d3f32-f23f-2'

CLIENT_ID = ''
CLIENT_SECRET = ''
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
    scope = 'user-library-read user-read-private user-read-email'
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': scope,
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
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        response = requests.post(TOKEN_URL, data=req_body)
        #, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        
        token_info = response.json()
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        return redirect('/playlists')


@app.route('/playlists')
def me():
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect(url_for('/refresh-token'))
    
    response = requests.get(API_BASE_URL + 'me/playlists', headers={'Authorization': f"Bearer {session['access_token']}"})
    playlists = response.json()

    return jsonify(playlists)


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    response = requests.post(TOKEN_URL, data={
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token'],
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })

    new_token_info = response.json()
    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

    return redirect(url_for('me'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
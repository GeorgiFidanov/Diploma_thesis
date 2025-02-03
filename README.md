# Diploma_thesis
Diploma thesis for TUES 24'

# Reflex app with Spotify Authentication, Cosmos DB Integration, OpenAI response generation and Location API requests 

This project demonstrates the AI's possibilities to interact with the user and the Spotify API.


# Endpoints

 -   / Home page with a link to initiate Spotify login.
 -   /features: Displays the features of the app.
 -   /location_search: Retrieves and displays events near the user location.
 -   /playlists: Retrieves and displays user playlists.
 -   /new_playlist: Creates a new playlist based on the user's selection and input.
 -   /previous_conversations: Retrieves and displays previous conversations with the user.

## Introduction
The app will be accessible at http://localhost:1234.

## Features

-   User authentication via Spotify.
-   Retrieving user playlists and storing them in Cosmos DB.
-   Finds events near user.
-   Retrieving previous conversations with the user.
-   Creating a new playlist based on user input.


## Usage
Install dependencies:
- pip install -r requirements.txt

Find keys and secrets and store them in a local .env file
- CLIENT_ID = ''
- CLIENT_SECRET = ''
- AccountEndpoint = ''
- AccountKey = ''
- DatabaseName = ''
- ContainerName = ''
- OpenAiKey = ''
- LOCATION_API_KEY = ''

Create a Spotify app at 'https://developer.spotify.com/dashboard'
- set the redirect URI to http://localhost:1234/

Init the Reflex files
- reflex init

Run the application:
- reflex run

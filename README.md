# Diploma_thesis
Diploma thesis for TUES 24'

# Flask Spotify Authentication and Cosmos DB Integration

This project demonstrates the integration of Spotify authentication with a Flask web application and storage of user data in Azure Cosmos DB.


# Endpoints

 -   /: Home page with a link to initiate Spotify login.
 -   /login: Redirects to Spotify for user authentication.
 -   /callback: Spotify callback to handle authorization code and store user tokens.
 -   /playlists: Retrieves and displays user playlists.
 -   /refresh-token: Refreshes the Spotify access token.
 -   /user: Handles user selection of a playlist, creates a new user profile, and stores it in Cosmos DB.

## Introduction
The app will be accessible at http://localhost:5000.

## Features

-   User authentication via Spotify.
-   Retrieving user playlists and storing them in Cosmos DB.
-   Checking for existing users in Cosmos DB before creating new profiles.

## Usage
Install dependencies:
- pip install -r requirements.txt

Run the application:
- python run.py

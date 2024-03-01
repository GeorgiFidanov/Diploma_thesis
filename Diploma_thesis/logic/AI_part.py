from Diploma_thesis.logic.DB_logic import edit_user
import openai
from dotenv import load_dotenv
import os


load_dotenv()
OpenAiKey = os.getenv("OpenAiKey")
openai.api_key = OpenAiKey


def generate_recommendations(user_id, song_infos, playlist_name, user_input):
    """Generates a new playlist based on the features given by a user.
    If a user doesn't provide a name for the playlist, generates one.
    Returns a list of songs which are be added to the playlist."""

    # Divide the songs into batches
    batch_size = 10
    batches = [song_infos[i:i + batch_size] for i in range(0, len(song_infos), batch_size)]
    recommended_songs_set = set()

    for batch in batches:
        batch_songs = []
        for song in batch:

            # Convert the batch into a string
            current_song = "\n".join([f"\
            Name: {song['name']}, Artist: {song['artist_name']}, Album: {song['album_name']}, \
            External URL: {song['external_url']}, Acousticness: {song['acousticness']}, \
            Danceability: {song['danceability']}, Energy: {song['energy']}, \
            Instrumentalness: {song['instrumentalness']}, Key: {song['key']}, \
            Liveness: {song['liveness']}, Loudness: {song['loudness']}, \
            Speechiness: {song['speechiness']}, Tempo: {song['tempo']}, Valence: {song['valence']}\n"])
            batch_songs.append(current_song)

        # Make a new request for each batch of songs
        prompt = f"""
        You are in the role of a professional music search engine.
        You will be given indepth information for several songs.
        You will then be asked to generate recommendations for new songs.
        Each song that you generate must correspond to one of the songs given earlier.
        Each new song must have similar characteristics to the information given
        but preferably from a different artist and album.
        Provide only the song names and artist names of the recommended songs in the following format:
        Song - Artist
        Please do not place a number before the song name.
        Here is the information for up to 10 songs:
        {batch_songs}
        Bonus requarents: {user_input}
        """
    
        # Generate the response
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.2
        )
    
        # Extract the recommended songs from the response
        batch_recommended_songs = response.choices[0].message.content.strip().split("\n")

        # Add the recommended songs to the list
        recommended_songs_set.update(batch_recommended_songs)

    recommended_songs = list(recommended_songs_set)

    # Generate a name for the playlist if the user hasn't given one
    if playlist_name == '':
        prompt = f"""Generate a name for your playlist:{recommended_songs}"""
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.2
        )
        playlist_name = response.choices[0].message.content.strip().split("\n")

    recommended_songs.insert(0, playlist_name)
    # Add the new responce to the history of the user
    edit_user(user_id, 'context', recommended_songs)
    return recommended_songs

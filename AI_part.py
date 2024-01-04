import openai
from dotenv import load_dotenv
import os

load_dotenv()
OpenAiKey = os.getenv("OpenAiKey")
openai.api_key = OpenAiKey


def generate_recommendations(song_infos):
    # Divide the songs into batches
    batch_size = 10
    batches = [song_infos[i:i + batch_size] for i in range(0, len(song_infos), batch_size)]

    # Initialize an empty list to store the recommended songs
    recommended_songs = []

    for batch in batches:
        for song_info in batch:
        # Convert the batch into a string
            batch_str = "\n".join([ f"Name: {song_info['name']}, Artist: {song_info['artist_name']},
                                    Album: {song_info['album_name']},
                                    External URL: {song_info['external_url']},
                                    Acousticness: {song_info['acousticness']},
                                    Danceability: {song_info['danceability']},
                                    Energy: {song_info['energy']},
                                    Instrumentalness: {song_info['instrumentalness']},
                                    Key: {song_info['key']}, Liveness: {song_info['liveness']},
                                    Loudness: {song_info['loudness']},
                                    Speechiness: {song_info['speechiness']},
                                    Tempo: {song_info['tempo']},
                                    Valence: {song_info['valence']}\n"])
  
        prompt = f"""
        Based on the following songs:
        {batch_str}
        Generate recommendations for 10 new songs. Each song corresponds to one of the songs given earlier.
        Each of these new songs from you must have similar characteristics
        to the corresponding song but preferably from a different artist, album, and genre.
        Also, the recommended songs should sound similar to the original songs.
        Provide the names and artist names of the recommended songs in the format "Song - Artist".
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
        recommended_songs.extend(batch_recommended_songs)

    return recommended_songs


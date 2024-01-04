import json

def extract_song_info(song_data):
   song_data_dict = song_data
   # Extracting relevant information
   try:
       name = song_data_dict["name"]
   except KeyError:
       name = None

   try:
       album_name = song_data_dict["album"]["name"]
   except KeyError:
       album_name = None

   try:
       artist_name = song_data_dict["artists"][0]["name"]
   except KeyError:
       artist_name = None

   try:
       danceability = song_data_dict["danceability"]
   except KeyError:
       danceability = None

   try:
       energy = song_data_dict["energy"]
   except KeyError:
       energy = None

   try:
       key = song_data_dict["key"]
   except KeyError:
       key = None

   try:
       tempo = song_data_dict["tempo"]
   except KeyError:
       tempo = None

   try:
       external_url = song_data_dict["external_urls"]["spotify"]
   except KeyError:
       external_url = None

   song_info = {
       "name": name,
       "album_name": album_name,
       "artist_name": artist_name,
       "danceability": danceability,
       "energy": energy,
       "key": key,
       "tempo": tempo,
       "external_url": external_url
   }

   return song_info
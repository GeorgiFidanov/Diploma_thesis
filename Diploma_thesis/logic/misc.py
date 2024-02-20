import ast
import json
import re


# Miscellaneous functions
def write_response_to_file(response, filename):
    """Writes data to a temporary file"""
    with open(filename, 'w') as f:
        json.dump(response, f)


def read_songs_from_file(file_path):
    """Reads the data from a temporary file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        songs_list = ast.literal_eval(content)
    return songs_list


def clear_temp_file():
    """Whipes the contents of temp.txt"""
    with open('temp.txt', 'w'):
        pass


# Note this method has 50% success rate at cleaning data, so it will be patched soon... 
def clean_song_list(song_list):
    """Cleans a list of songs by using a regular expression.
    It is meant to be used for cleaning the AI response data."""

    # Regular expression pattern to remove asterisks and other unwanted characters
    cleanup_pattern = re.compile(r'[*\[\]":,]')  # '\*|\[|\]|"|:|,'

    # Regular expression pattern to remove leading numbers, dots, and spaces
    leading_numbers_pattern = re.compile(r'^\s*\d+\.?\s*')

    # Regular expression pattern to split the song into artist and track name
    artist_track_pattern = re.compile(r'^(.*?) - (.*)$')

    # Use list comprehension to create a new list with cleaned song names
    cleaned_songs = [
        {
            'artist_name': artist_track_pattern.match(cleanup_pattern.sub('', song)).group(2).strip(),
            'track_name': artist_track_pattern.match(cleanup_pattern.sub('', song)).group(1).strip()
        }
        for song in song_list
        if song != 'Song - Artist' and artist_track_pattern.match(song)  # Remove the placeholder and invalid entries
    ]

    # Remove leading numbers, dots, and spaces from track names
    for song in cleaned_songs:
        song['track_name'] = leading_numbers_pattern.sub('', song['track_name'])

    return cleaned_songs

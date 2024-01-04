import ast


#30 songs will be max
def read_songs_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        songs_list = ast.literal_eval(content)
    return len(songs_list)
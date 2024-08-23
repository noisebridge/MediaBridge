# This script handles loading the movie titles and ratings data
import os

def load_movie_titles(filepath):
    movie_data = []
    with open(filepath, 'r', encoding='ISO-8859-1') as file:
        for line in file:
            movie_id, year, title = line.strip().split(",", 2)
            movie_data.append([int(movie_id), int(year), title])
    return movie_data

def load_ratings(directory_path):
    files = sorted([f for f in os.listdir(directory_path) if f.startswith('mv_')])
    return files

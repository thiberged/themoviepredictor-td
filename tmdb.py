import requests
import json
from pprint import pprint
from movie import Movie
from datetime import datetime
import locale
import isodate
import os

locale.setlocale(locale.LC_ALL, 'en_US')

class TheMoviedb:

    def __init__(self, api_key):
        self.api_key = api_key

    def tmdb_get_by_id(self, id, api_key):
        r = requests.get(f'https://api.themoviedb.org/3/movie/{id}?api_key={api_key}')
        r = r.json()
        if 'status_code' not in r:
            title = r['title']
            original_title = r['original_title']
            release_date = r['release_date']
            if r['adult'] == 'False':
                rating = 'TP'
            else:
                rating = '-18'
            duration = r['runtime']
            box_office = r['revenue']
            imdb_id = r['imdb_id']
            imdb_id = imdb_id.replace("tt", "")
            imdb_score = r['vote_average']
            # synopsis = r['overview']
            # production_budget = r['bugdet']
            movie = Movie(imdb_id, title, original_title, duration, release_date, rating, imdb_score, box_office)
            return movie
        if r['status_code'] == 34:
            movie = f"Aucun film avec l'id {id} n'existe dans TMDBapi"
            return movie

    # def omdb_gat_by_year(self, year):

# film = TheMoviedb(api_key_tmdb)
# Film = film.tmdb_get_by_id('550')
# print(Film)

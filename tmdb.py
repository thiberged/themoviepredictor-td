import requests
import json
from pprint import pprint
from movie import Movie
from datetime import datetime
import locale
import os
import app

# locale.setlocale(locale.LC_ALL, 'en_US')

class Tmdb:

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
            synopsis = r['overview']
            production_budget = r['budget']
            movie = Movie(title, original_title, release_date, duration, rating)
            movie.imdb_id = imdb_id
            movie.imdb_score = imdb_score
            movie.box_office = box_office

            actors = r['Actors']
            for actor in actors:
                firstname = actor[0]
                lastname = actor [1]

                app.insert_people(firstname, lastname)

            return movie
        if r['status_code'] == 34:
            movie = f"Aucun film avec l'id {id} n'existe dans la base"
            return movie

    def tmdb_get_actors(self, id, api_key):
        r = requests.get(f'https://api.themoviedb.org/3/movie/{id}?api_key={api_key}')
        r = r.json()
        if 'status_code' not in r:
            actors = r['Actors']
            for actor in actors:
                firstname = actor[0]
                lastname = actor [1]

                app.insert_people(firstname, lastname)

            return actors


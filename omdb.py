import requests
import json
from pprint import pprint
from movie import Movie
from datetime import datetime
import locale
import os

# locale.setlocale(locale.LC_ALL, 'en_US')

class Omdb:

    def __init__(self, api_key):
        self.api_key = api_key

    def omdb_get_by_id(self, id, api_key):
        r = requests.get(f'http://www.omdbapi.com/?i={id}&apikey={api_key}')
        r = r.json()
        if r['Response'] == "False":
            movie = f"Aucun film avec l'id {id} n'existe pas dans la base"
            return movie
        else:
            imdb_id_str = r['imdbID']
            imdb_id = imdb_id_str.replace("tt", "")
            title = r['Title']
            original_title = r['Title']
            release_date_class = r['Released']
            release_date_strip = release_date_class.strip()
            release_date_object = datetime.strptime(release_date_strip, '%d %b %Y')
            release_date = release_date_object.strftime('%Y-%m-%d')
            duration = r['Runtime']
            duration = duration.split()
            duration = duration[0]
            if r['Rated'] == 'R':
                rating = '-12'
            elif r['Rated'] == 'NC-17':
                rating = '-16'
            else:
                rating = 'TP'
            if r['Type']=="movie":
                box_office = r['BoxOffice']
                if r['BoxOffice'] == 'N/A':
                    box_office = None
            else:
                box_office = None
            imdb_score = r['imdbRating']

            movie = Movie(title, original_title, release_date, duration, rating)
            movie.imdb_id = imdb_id
            movie.imdb_score = imdb_score
            movie.box_office = box_office

            return movie

    def omdb_get_actors(self, id, api_key):
        r = requests.get(f'http://www.omdbapi.com/?i={id}&apikey={api_key}')
        r = r.json()

        print(r)
        actors = r['Actors']
        return actors
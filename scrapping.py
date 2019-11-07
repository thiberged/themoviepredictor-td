#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TheMoviePredictor script
Author: Arnaud de Mouhy <arnaud@admds.net>
"""

import mysql.connector
import sys
import argparse
import csv
import requests as rq
import auth_env as ae
import json
from html.parser import HTMLParser
from datetime import datetime

import html

from movie import Movie
from person import Person

def connectToDatabase():
    return mysql.connector.connect(user='predictor', password='predictor',
                              host='127.0.0.1',
                              database='predictor')

def disconnectDatabase(cnx):
    cnx.close()

def createCursor(cnx):
    return cnx.cursor(dictionary=True)

def closeCursor(cursor):    
    cursor.close()

def findQuery(table, id):
    return ("SELECT * FROM {} WHERE id = {} LIMIT 1".format(table, id))

def find_movie(title, date):
    return (f"SELECT * FROM `movies` WHERE `title` = {title} AND `release_date` = {date}")

def findAllQuery(table):
    return ("SELECT * FROM {}".format(table))

def insert_people_query(firstname, lastname):
    return (f"INSERT INTO `people` (`firstname`, `lastname`) VALUES ('{firstname}', '{lastname}');")

def insert_movie_query(movie):
    return (f"INSERT INTO `movies` (`title`, `original_title`, `duration`, `rating`, `release_date`) VALUES ('{movie.title}', '{movie.original_title}', {movie.duration}, '{movie.rating}', '{movie.release_date}');")

def db_movie_query(movie):
    return (f"INSERT INTO `movies` (`title`, `original_title`, `synopsis`, `duration`, `rating`, `release_date`) VALUES ('{movie.title}', '{movie.original_title}', '{movie.synopsis}', {movie.duration}, '{movie.rating}', '{movie.release_date}');")

def find(table, id):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    query = findQuery(table, id)
    cursor.execute(query)
    results = cursor.fetchall()

    entity = None
    if (cursor.rowcount == 1):
        row = results[0]
        if (table == "movies"):
            entity = Movie(row['title'], row['original_title'], row['duration'], row['release_date'], row['rating'])
            entity.id = row['id']
        if table == "people":
            entity = Person(row['firstname'], row['lastname'])
            entity.id = row['id']

    closeCursor(cursor)
    disconnectDatabase(cnx)

    return entity

def findAll(table):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    cursor.execute(findAllQuery(table))
    results = cursor.fetchall() # liste de dictionnaires contenant des valeurs scalaires
    closeCursor(cursor)
    disconnectDatabase(cnx)
    if (table == "movies"):
        movies = []
        for result in results: # result: dictionnaire avec id, title, ...
            movie = Movie(
                title=result['title'],
                original_title=result['original_title'],
                duration=result['duration'],
                release_date=result['release_date'],
                rating=result['rating']
            )
            movie.id = result['id']
            movies.append(movie)
        return movies
    if table == "people":
        people = []
        for result in results: # result: dictionnaire avec id, firstname, ...
            person = Person(
                firstname=result['firstname'],
                lastname=result['lastname'],
            )
            person.id = result['id']
            people.append(person)
        return people

def insert_people(firstname, lastname):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    cursor.execute(insert_people_query(firstname, lastname))
    cnx.commit()
    last_id = cursor.lastrowid
    closeCursor(cursor)
    disconnectDatabase(cnx)
    return last_id

def insert_movie(movie):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    cursor.execute(insert_movie_query(movie))
    cnx.commit()
    last_id = cursor.lastrowid
    closeCursor(cursor)
    disconnectDatabase(cnx)
    return last_id

def db_movie(movie):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    cursor.execute(db_movie_query(movie))
    cnx.commit()
    last_id = cursor.lastrowid
    closeCursor(cursor)
    disconnectDatabase(cnx)
    return last_id

def printPerson(person):
    print("#{}: {} {}".format(person.id, person.firstname, person.lastname))

def printMovie(movie):
    print("#{}: {} released on {}".format(movie.id, movie.title, movie.release_date))

def GET_tmdb_movie(title, date):
    request_id = rq.get(f"https://api.themoviedb.org/3/search/movie?api_key={ae.tmp_api_key}&query={title}&year={date}")
    page_id = request_id.text
    jpage = json.loads(page_id)
    res  = jpage['results']
    info = res[0]
    id = info['id']

    request_movie = rq.get(f"https://api.themoviedb.org/3/movie/{id}?api_key={ae.tmp_api_key}&language=fr")
    page = request_movie.text
    return json.loads(page)

def GET_omdb_movie(title, date):
    request_id = rq.get(f"http://www.omdbapi.com/?apikey={ae.omdb_api_key}&s={title}&y={date}")
    page_id = request_id.text
    jpage = json.loads(page_id)
    res  = jpage['Search']
    info = res[0]
    id = info['imdbID']

    request_movie = rq.get(f"http://www.omdbapi.com/?apikey={ae.omdb_api_key}&i={id}")
    page = request_movie.text
    return json.loads(page)

parser = argparse.ArgumentParser(description='Process MoviePredictor data')

parser.add_argument('context', choices=('people', 'movies'), help='Le contexte dans lequel nous allons travailler')

action_subparser = parser.add_subparsers(title='action', dest='action')

tmdb_parser = action_subparser.add_parser('tmdb', help='Insert une nouvelle entité depuis tmdb')
tmdb_parser.add_argument('--title' , help='Titre en France', required=True)
tmdb_parser.add_argument('--release' , help='année de sortie', required=True)

omdb_parser = action_subparser.add_parser('omdb', help='Insert une nouvelle entité depuis omdb')
omdb_parser.add_argument('--title' , help='Titre en France', required=True)
omdb_parser.add_argument('--release' , help='année de sortie', required=True)

list_parser = action_subparser.add_parser('list', help='Liste les entitées du contexte')
list_parser.add_argument('--export' , help='Chemin du fichier exporté')

find_parser = action_subparser.add_parser('find', help='Trouve une entité selon un paramètre')
find_parser.add_argument('id' , help='Identifant à rechercher')

import_parser = action_subparser.add_parser('import', help='Importer un fichier CSV')
import_parser.add_argument('--file', help='Chemin vers le fichier à importer', required=True)

insert_parser = action_subparser.add_parser('insert', help='Insert une nouvelle entité')
known_args = parser.parse_known_args()[0]

if known_args.context == "people":
    insert_parser.add_argument('--firstname' , help='Prénom de la nouvelle personne', required=True)
    insert_parser.add_argument('--lastname' , help='Nom de la nouvelle personne', required=True)

if known_args.context == "movies":
    insert_parser.add_argument('--title' , help='Titre en France', required=True)
    insert_parser.add_argument('--duration' , help='Durée du film', type=int, required=True)
    insert_parser.add_argument('--original-title' , help='Titre original', required=True)
    insert_parser.add_argument('--release-date' , help='Date de sortie en France', required=True)
    insert_parser.add_argument('--rating' , help='Classification du film', choices=('TP', '-12', '-16'), required=True)

args = parser.parse_args()

if args.context == "people":
    if args.action == "list":
        people = findAll("people")
        if args.export:
            with open(args.export, 'w', encoding='utf-8', newline='\n') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(people[0].keys())
                for person in people:
                    writer.writerow(person.values())
        else:
            for person in people:
                printPerson(person)
    if args.action == "find":
        peopleId = args.id
        people = find("people", peopleId)
        if (people == None):
            print(f"Aucune personne avec l'id {peopleId} n'a été trouvée ! Try Again!")
        else:
            printPerson(people)
    if args.action == "insert":
        print(f"Insertion d'une nouvelle personne: {args.firstname} {args.lastname}")
        people_id = insert_people(firstname=args.firstname, lastname=args.lastname)
        print(f"Nouvelle personne insérée avec l'id '{people_id}'")

if args.context == "movies":
    if args.action == "list":  
        movies = findAll("movies")
        for movie in movies:
            printMovie(movie)
    if args.action == "find":  
        movieId = args.id
        movie = find("movies", movieId)
        if (movie == None):
            print(f"Aucun film avec l'id {movieId} n'a été trouvé ! Try Again!")
        else:
            printMovie(movie)
    if args.action == "insert":
        print(f"Insertion d'un nouveau film: {args.title}")
        movie = Movie(args.title, args.original_title, args.duration, args.release_date, args.rating)
        movie_id = insert_movie(movie)
        print(f"Nouveau film inséré avec l'id '{movie_id}'")
    if args.action == "tmdb":
        print(f"Insertion d'un nouveau film depuis tmdb : {args.title} ({args.release})")
        info = GET_tmdb_movie(args.title, args.release)

        title = info['title']
        release_date = info['release_date']
        original_title = info['original_title']
        synopsis = info['overview']
        note = info['vote_average']
        duration = info['runtime']
        vote = info['vote_count']
        boxoffice = info['revenue']
        rating = "TP"

        movie = Movie(title, original_title, release_date, duration, rating)
        movie.synopsis = synopsis
        movie.vote = vote
        movie.boxoffice = boxoffice

        if not find_movie(title, release_date):
            movie_id = db_movie(movie)
            print(f"Nouveau film inséré avec l'id '{movie_id}'")
        else:
            print("Le film est déjà enregistré")
    if args.action == "omdb":
        print(f"Insertion d'un nouveau film depuis omdb : {args.title} ({args.release})")
        info = GET_omdb_movie(args.title, args.release)

        title = info['Title']
        release_date_object = info['Released']
        release_date_sql_string = datetime.strptime(release_date_object,'%d %b %Y').date()
        release_date = release_date_sql_string.strftime('%Y-%m-%d')
        original_title = title
        synopsis = info['Plot']
        note = info['imdbRating']
        duration_splitted = info['Runtime'].split('m')
        duration = int(duration_splitted[0])
        vote = info['imdbVotes']
        boxoffice = info['BoxOffice']
        rating = "TP"

        movie = Movie(title, original_title, release_date, duration, rating)
        movie.synopsis = synopsis
        movie.vote = vote
        movie.boxoffice = boxoffice

        if not find_movie(title, release_date):
            movie_id = db_movie(movie)
            print(f"Nouveau film inséré avec l'id '{movie_id}'")
        else:
            print("Le film est déjà enregistré")
    if args.action == "import":
        with open(args.file, 'r', encoding='utf-8', newline='\n') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                movie_id = insert_movie(
                    title=row['title'],
                    original_title=row['original_title'],
                    duration=row['duration'],
                    rating=row['rating'],
                    release_date=row['release_date']
                )
                print(f"Nouveau film inséré avec l'id '{movie_id}'")
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
import os
import locale
import random

import html

from movie import Movie
from person import Person
from omdb import Omdb
from tmdb import Tmdb

# locale.setlocale(locale.LC_ALL, 'fr_FR')

api_key_tmdb = os.environ['TMDB_API_KEY']
tmdb = Tmdb(api_key_tmdb)

api_key_omdb = os.environ['OMDB_API_KEY']
omdb = Omdb(api_key_omdb)

def connectToDatabase():
    passw = os.environ['MYSQL_PASSWORD']
    return mysql.connector.connect(user='predictor', password=passw,
                              host='database',
                              database='predictor')

def disconnectDatabase(cnx):
    cnx.close()

def createCursor(cnx):
    return cnx.cursor(dictionary=True)

def closeCursor(cursor):    
    cursor.close()

def findQuery(table, id):
    return (f"SELECT * FROM {table} WHERE id = {id} LIMIT 1")

def find_movie_query(title, date):
    return (f"SELECT * FROM `movies` WHERE `title` = {title} AND `release_date` = {date}")

def findAllQuery(table):
    return (f"SELECT * FROM {table}")

def insert_people_query(firstname, lastname):
    return (f"INSERT INTO `people` (`firstname`, `lastname`) VALUES ('{firstname}', '{lastname}');")

def insert_movie_query(movie):
    add_movie = ("INSERT INTO movies "
                "(title, original_title, release_date, duration, rating) "
                "VALUES (%s, %s, %s, %s, %s)")
    data_movie = (movie.title, movie.original_title, movie.release_date, movie.duration, movie.rating)
    return (add_movie, data_movie)

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
            entity = Movie(row['title'], row['original_title'], row['release_date'], row['duration'], row['rating'])
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
                release_date=result['release_date'],
                duration=result['duration'],                
                rating=result['rating']
            )
            movie.imdb_id = result['imdb_id']
            movie.imdb_score = result['imdb_score']
            movie.boxoffice = result['box_office']
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
    add_movie, data_movie = insert_movie_query(movie)
    cursor.execute(add_movie, data_movie)
    last_id = cursor.lastrowid
    cnx.commit()
    closeCursor(cursor)
    disconnectDatabase(cnx)
    return last_id

def printPerson(person):
    print(f"#{person.id}: {person.firstname} {person.lastname}")

def printMovie(movie):
    print(f"#{movie.id}: {movie.title} released on {movie.release_date}")

parser = argparse.ArgumentParser(description='Process MoviePredictor data')

parser.add_argument('context', choices=('people', 'movies'), help='Le contexte dans lequel nous allons travailler')

action_subparser = parser.add_subparsers(title='action', dest='action')

list_parser = action_subparser.add_parser('list', help='Liste les entitées du contexte')
list_parser.add_argument('--export' , help='Chemin du fichier exporté')

find_parser = action_subparser.add_parser('find', help='Trouve une entité selon un paramètre')
find_parser.add_argument('id' , help='Identifant à rechercher')

insert_parser = action_subparser.add_parser('insert', help='Insert une nouvelle entité')

import_parser = action_subparser.add_parser('import', help='Importer un fichier CSV')
import_parser.add_argument('--file', help='Chemin vers le fichier à importer')
import_parser.add_argument('--api', help='nom de API utilisée')

known_args = parser.parse_known_args()[0]

if known_args.api == 'omdb':
    year_parser = import_parser.add_argument('--year', help='année des films recherchés')
    imdbId_parser = import_parser.add_argument('--imdb_id', help='Id du film recherché sur API')

if known_args.api == 'tmdb':
    year_parser = import_parser.add_argument('--year', help='année des films recherchés')
    imdbId_parser = import_parser.add_argument('--imdb_id', help='Id du film recherché sur API')

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
        movie = Movie(args.title, args.original_title, args.release_date, args.duration, args.rating)
        movie_id = insert_movie(movie)
        print(f"Nouveau film inséré avec l'id '{movie_id}'")
    if args.action == "import":
        if args.api == 'omdb':
            if args.imdb_id :
                movie = omdb.omdb_get_by_id(args.imdb_id, api_key_omdb)
                movie_id = insert_movie(movie)
                print(f"Nouveau film inséré avec l'id {movie_id}")
                actors = omdb.omdb_get_actors(args.imdb_id, api_key_omdb)
                for actor in actors:
                    firstname = actor[0]
                    lastname = actor [1]

                    insert_people(firstname, lastname)
            if not args.imdb_id :
                n = 0
                while n == 0:
                    imdb_id = "tt" + str(random.randint(0,9999999)).rjust(7,'0')
                    movie = omdb.omdb_get_by_id(imdb_id, api_key_omdb)
                    if type(movie) != str:
                        n = 1
                movie_id = insert_movie(movie)
                print(f"Nouveau film inséré avec l'id {movie_id}")
                actors = omdb.omdb_get_actors(args.imdb_id, api_key_omdb)
                for actor in actors:
                    firstname = actor[0]
                    lastname = actor [1]

                    insert_people(firstname, lastname)
        if args.api == 'tmdb':
            if args.imdb_id :
                movie = tmdb.tmdb_get_by_id(args.imdb_id, api_key_tmdb)
                movie_id = insert_movie(movie)
                print(f"Nouveau film inséré avec l'id {movie_id}")
            if not args.imdb_id :
                n = 0
                while n == 0:
                    imdb_id = "tt" + str(random.randint(0,9999999)).rjust(7,'0')
                    movie = tmdb.tmdb_get_by_id(imdb_id, api_key_tmdb)
                    if type(movie) != str:
                        n = 1
                movie_id = insert_movie(movie)
                print(f"Nouveau film inséré avec l'id {movie_id}")
        if not args.api:
            with open(args.file, 'r', encoding='utf-8', newline='\n') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    movie_id = insert_movie(
                        title=row['title'],
                        original_title=row['original_title'],
                        release_date=row['release_date'],
                        duration=row['duration'],
                        rating=row['rating']                        
                    )
                    print(f"Nouveau film inséré avec l'id '{movie_id}'")

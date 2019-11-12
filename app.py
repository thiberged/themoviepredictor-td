#!/usr/bin/python 
# --> (c'est un shebang)
# -*- coding: utf-8 -*-

"""
TheMoviePredictor script
Author: Arnaud de Mouhy <arnaud@admds.net>
"""

import mysql.connector
import sys
import argparse
import csv
import requests
from bs4 import BeautifulSoup
from pprint import pprint 
from datetime import datetime
import locale
import os

from movie import Movie
from person import Person
from omdb import Omdb
from tmdb import Tmdb

locale.setlocale(locale.LC_ALL, 'fr_FR')

api_key_tmdb = os.environ['TMDB_API_KEY']
tmdb = TheMoviedb(api_key_tmdb)

api_key_omdb = os.environ['OMDB_API_KEY']
omdb = Omdb(api_key_omdb)

def connect_to_database():
    password = os.environ['MYSQL_PASSWORD']
    return mysql.connector.connect(user='predictor', 
                                password=password,
                                host='database',
                                database='predictor')

def disconnect_database(cnx):
    cnx.close()

def create_cursor(cnx):
    return cnx.cursor(dictionary=True)

def close_cursor(cursor):    
    cursor.close()

def find_query(table, id):
    return (f"SELECT * FROM {table} WHERE id = {id} LIMIT 1")

def find_all_query(table):
    return (f"SELECT * FROM {table}")

def find(table, id):
    cnx = connect_to_database()
    cursor = create_cursor(cnx)
    query = find_query(table, id)
    cursor.execute(query)
    results = cursor.fetchall()
    entity = None
    if (table == "movies"):
        if (cursor.rowcount == 1):
            row = results[0]
            entity = Movie(row['imdb_id'],
                        row['title'],
                        row['original_title'],
                        row['duration'],
                        row['release_date'],
                        row['rating'],
                        row['imdb_score'],
                        row['box_office'] 
            )
            entity.id = row['id']
    if (table == "people"):
        if (cursor.rowcount == 1):
            row = results[0]
            entity = Person(row['firstname'],
                            row['lastname'],
            )
            entity.id = row['id']
    close_cursor(cursor)
    disconnect_database(cnx)
    return entity

def find_all(table):
    cnx = connect_to_database()
    cursor = create_cursor(cnx)
    cursor.execute(find_all_query(table))
    results = cursor.fetchall() # liste de dictionnaires contenant des valeurs scalaires
    close_cursor(cursor)
    disconnect_database(cnx)
    if (table == "movies"):
        movies = []
        for result in results: # dico avec Id, title...
            movie = Movie(
                imdb_id = result['imdb_id'], 
                title = result['title'], 
                original_title = result['original_title'],
                duration = result['duration'],
                release_date = result['release_date'],
                rating = result['rating'],
                imdb_score = result['imdb_score'],
                box_office = result['box_office']
            )
            movie.id = result['id']
            movies.append(movie)
        return movies
    if (table == "people"):
        people = []
        for result in results: # dico avec Id, firstname...
            person = Person(
                firstname = result['firstname'], 
                lastname = result['lastname'],
            )
            person.id = result['id']
            people.append(person)
        return people

def insert_people_query(person):
    add_person = ("INSERT INTO people "
                "(firstname, lastname) "
                "VALUES (%s, %s)")
    data_person = (person.firstname, person.lastname)
    return (add_person, data_person)

def insert_people(person):
    # pas besoin de signifier la table car c'est forcément la table People
    cnx = connect_to_database()
    cursor = create_cursor(cnx)
    add_person, data_person = insert_people_query(person)
    cursor.execute(add_person, data_person)
    person.id = cursor.lastrowid
    cnx.commit()
    close_cursor(cursor)
    disconnect_database(cnx)
    return cursor.lastrowid

def insert_movie_query(movie):
    add_movie = ("INSERT INTO movies "
                "(imdb_id, title, original_title, duration, release_date, rating, imdb_score, box_office) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    data_movie = (movie.imdb_id, movie.title, movie.original_title, movie.duration, movie.release_date, movie.rating, movie.imdb_score, movie.box_office)
    return (add_movie, data_movie)

def insert_movie(movie):
    cnx = connect_to_database()
    cursor = create_cursor(cnx)
    add_movie, data_movie = insert_movie_query(movie)
    cursor.execute(add_movie, data_movie)
    movie.id = cursor.lastrowid
    cnx.commit()
    close_cursor(cursor)
    disconnect_database(cnx)
    return cursor.lastrowid

def print_person(person):
    print(f"#{person.id}: {person.firstname} {person.lastname}")

def print_movie(movie):
    print(f"#{movie.id}: {movie.title} released on {movie.release_date}")

parser = argparse.ArgumentParser(description='Process MoviePredictor data')

parser.add_argument('context', choices=['people', 'movies'], help='Le contexte dans lequel nous allons travailler')

action_subparser = parser.add_subparsers(title='action', dest='action')

list_parser = action_subparser.add_parser('list', help='Liste les entitÃ©es du contexte')
list_parser.add_argument('--export' , help='Chemin du fichier exportÃ©')

find_parser = action_subparser.add_parser('find', help='Trouve une entitÃ© selon un paramÃ¨tre')
find_parser.add_argument('id' , help='Identifant Ã  rechercher')

insert_parser = action_subparser.add_parser('insert', help='insérer une donnée dans la database')

import_parser = action_subparser.add_parser('import', help='Importer de nouvelles données')
import_parser.add_argument('--file', help='nom du fichier à recuperer')
import_parser.add_argument('--api', help='nom de API utilisée')

know_args = parser.parse_known_args()[0]

if know_args.api == 'omdb':
    year_parser = import_parser.add_argument('--year', help='année des films recherchés')
    imdbId_parser = import_parser.add_argument('--imdb_id', help='Id du film recherché sur API')

if know_args.api == 'themoviedb':
    year_parser = import_parser.add_argument('--year', help='année des films recherchés')
    imdbId_parser = import_parser.add_argument('--imdb_id', help='Id du film recherché sur API')


if know_args.context == "people":
    insert_parser.add_argument('--firstname', help='prenom', required=True)
    insert_parser.add_argument('--lastname', help='nom de famille', required=True)

if know_args.context == "movies":
    insert_parser.add_argument('--title', help='le titre en france', required=True)
    insert_parser.add_argument('--original_title', help='titre original', required=True)
    insert_parser.add_argument('--synopsis', help='le synopsis du film')
    insert_parser.add_argument('--duration', help='la durée en minute du film', required=True)
    insert_parser.add_argument('--rating', help='la classification pour visionnage du public', choices=('TP', '-12', '-16', '-18'), required=True)
    insert_parser.add_argument('--production_budget', help='le budget du film')
    insert_parser.add_argument('--marketing_budget', help='le budget pour la promo du film')
    insert_parser.add_argument('--release_date', help='la date de sortie', required=True)    

args = parser.parse_args()

if args.context == "people":
    if args.action == "list":
        people = find_all("people")
        if args.export:
            with open(args.export, 'w', encoding='utf-8', newline='\n') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(people[0].__dict__.keys())
                for person in people:
                    writer.writerow(person.__dict__.values())
        else:
            for person in people:
                print_person(person)
    if args.action == "find":
        peopleId = args.id
        person = find("people", peopleId)
        if (person == None):
            print(f"Aucune personne avec l'id {peopleId} n'a été trouvé ! Try again !")
        else:
            print_person(person)
    if args.action == "insert":
        person = Person(args.firstname, 
                        args.lastname, 
        )
        person.id = insert_people(person)
        insert_people(person)
        print('insert')

if args.context == "movies":
    if args.action == "list":  
        movies = find_all("movies")
        for movie in movies:
            print_movie(movie)
    if args.action == "find":  
        movieId = args.id
        movie = find("movies", movieId)
        if (movie == None):
            print(f"Aucun film avec l'id {movieId} n'a été trouvé ! Try again !")
        else:
            print_movie(movie)
    if args.action == "insert":
        movie = Movie(args.title, 
                    args.original_title, 
                    args.duration, 
                    args.release_date, 
                    args.rating,
                    args.box_office,
                    args.imdb_id, 
                    args.imdb_score
        )
        movie.id = insert_movie(movie)
        print('insert')

    # action "import", pour importer une base de données à partir d'un fichier csv ou à partir d'une API

    if args.action == "import":
        # if args.file:
        #     with open(args.file) as csvfile:
        #         csv_reader = csv.DictReader(csvfile, delimiter=',')
        #         for row in csv_reader:
        #             insert_movie(
        #                 row['title'], 
        #                 row['original_title'], 
        #                 row['duration'], 
        #                 row['rating'], 
        #                 row['release_date'],
        #                 row['box_office'],
        #                 row['imdb_id'], 
        #                 row['imdb_score']
        #             )
        #             print(', '.join(row))
        if args.api == 'omdb':
            if args.imdb_id :
                movie = omdb.omdb_get_by_id(args.imdb_id, api_key_omdb)
                insert_movie(movie)
                print(f"insert {movie.id}")
        if args.api == 'themoviedb':
            if args.imdb_id :
                movie = tmdb.tmdb_get_by_id(args.imdb_id, api_key_tmdb)
                insert_movie(movie)
                print(f"insert {movie.id}")
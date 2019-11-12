# The movie predictor

Ce projet doit nous permettre de prédire la critique qu'aura un film deux semaines apès sa sortie.

## Getting Started

Prendre une copie complète du fichier. Créer dans le répertoire du fichier un fichier auth.env contenant vos identifiants omdb et tmdb.

### Prerequisites

vscode
docker
github


## Running the tests

Dans le répertoire du fichier, ouvrir une fen^tre de commande bash. Puis taper la commande :
docker exec -it "nom du container" sh
puis :
python app.py "nom table" "nom action" "arguments supplémentaires"

### Break down into end to end tests

il est possible :
    - d'obtenir :
        - la liste des personnes de la table People
        - une personne particulière de la table People
        - la liste des films de la table Movies
        - un film en particulier de la table Movies
    - d'insérer :
        - une personne
        - un film
    - d'importer :
        - un film depuis omdb
        - un film depuid tmdb

### And coding style tests

Test effectués afin de remplir la base de donnée du projet tout en se préparant à pouvoir récupérer les dernier film le jour de leurs sortie.

### file and explain

app.py -> fichier principal de l'application
auth_env.py et auth.env -> contiennent les identifiants dans des variables d'environnements
docker-compose.yml -> structure de notre application
dockerfile -> configuration du lancement de l'application
movie.py, person.py -> classe permettant de stocker des données avant de les envoyer vers la base 
MovieFactory.py, PersonFactory.py -> classe contanant les différentes requêtes passé sur leurs classes correspondantes
omdb.py, tmdb.py -> classe permettant de stocker les données récupérer au niveau des api

## Versioning

We use python v3. 




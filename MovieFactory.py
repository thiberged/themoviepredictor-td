def isExist(title, date):
    return (f"SELECT * FROM `movies` WHERE `title` = {title} AND `release_date` = {date}")

def isExistById(id):
    return (f"SELECT * FROM `movies` WHERE `id` = {id} LIMIT 1")

def findAll():
    return ("SELECT * FROM `movies`")

def insert_movie(movie):
    request = (f"INSERT INTO `movies` (`title`, `original_title`, `synopsis`, `duration`, `rating`, `production_budget`, `marketing_budget`, `release_date`, `3d`)
                 VALUES ('{movie.title}', '{movie.original_title}', {movie.duration}, '{movie.rating}', '{movie.release_date}');")
    movie_data = (movie.title, movie.original_title, movie.synopsis, movie.duration, movie.rating,
                     movie.production_budget, movie.marketing_budget, movie.release_date, movie.3d)

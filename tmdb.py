import logging
import re
import time

import tmdbsimple as tmdb
from requests import HTTPError
from tinydb import operations, Query

import repository
from RateLimitedDecorator import RateLimited

WRONG_COLECAO_BEGINNING_OF_MOVIE_TITLE = "Coleção.*:\s*"
TITLE_ENDING_UNNECESSARY_NUMBER_ONE = "\s*1$"
tmdb.API_KEY = 'edc5f123313769de83a71e157758030b'


@RateLimited(4)
def searchMovie(name, year=''):
    try:
        return tmdb.Search().movie(query=name, language='pt-BR', year=year)['results'][0]['id']
    except IndexError:
        logging.error("No result found for query(movie-name: {}, year: {}".format(name, year))
        return None

@RateLimited(4)
def movie_info(movie_id):
    if movie_id:
        return tmdb.Movies(id=movie_id).info(language='pt-BR')


def fill_movie_data():
    movie_data = repository.movie_data()
    movies = repository.movies()
    no_data_movies = repository.no_data_movies()

    not_processed_movies = movies.search(Query().movie_data_id == 'NOT_PROCESSED')
    logging.debug("List for movie fill process: {}".format(not_processed_movies))
    for movie in not_processed_movies:
        title = movie['tvg_name']
        title, year = find_year_in_title(title)
        # TODO: Spell check movie name
        try:
            movie_id = searchMovie(clean_movie_title(title), year)
            movie_data_id = movie_data.upsert(movie_info(movie_id), Query().id == movie_id)
            movies.update(operations.set('movie_data_id', movie_data_id[0]), doc_ids=[movie.doc_id])
        except IndexError:
            logging.error("No results found for: {}".format(movie['tvg_name']))
            no_data_movies.upsert(movie, Query().tvg_name == movie.tvg_name and Query.movie_data_id != 'FIXED')
            movies.update(operations.set('movie_data_id', 'NO_DATA_FOUND'), doc_ids=[movie.doc_id])
        except HTTPError as e:
            logging.error("Error on TMDB request - {}".format(e.response))
            time.sleep(10)


def find_year_in_title(title):
    year = ''
    pattern_year_in_title = "\s+([0-9]{4})$"
    # Find year of movie and remove from query
    match = re.search(pattern_year_in_title, title)
    if match:
        year = match.group(1)
        title = re.sub(pattern_year_in_title, '', title)
    return title, year


def clean_movie_title(name):
    # Remove number 1 from first movie of trilogy
    cleaned_name = re.sub(TITLE_ENDING_UNNECESSARY_NUMBER_ONE, '', name)
    # Remove wrong beginning of movie name
    cleaned_name = re.sub(WRONG_COLECAO_BEGINNING_OF_MOVIE_TITLE, '', cleaned_name)
    # Remove wrong end of movie name
    # name = re.sub(":\s.*$", '', name)
    cleaned_name = re.sub("\s\(.*\)$", '', cleaned_name)
    cleaned_name = re.sub("\s+-.*", '', cleaned_name)
    return cleaned_name


'''
def fill_series_data():
    series = repository.series()
    not_processed_series = series.search(where('movie_id') == 'NOT_PROCESSED')
    for serie in not_processed_series:
        title = serie['tvg_name']
        title, year = find_year_in_title(title)
        # TODO: Spell check movie name
        try:
            movie_id = searchMovie(clean_movie_title(title), year)
            movie_data_id = movie_data.insert(movie_info(movie_id))
            movies.update(operations.set('movie_id', movie_data_id), doc_ids=[serie.doc_id])
        except IndexError:
            logging.error("No results found for: {}".format(serie['tvg_name']))
            no_data_movies.insert(serie)
            movies.update(operations.set('movie_id', 'NO_DATA_FOUND'), doc_ids=[serie.doc_id])
        except HTTPError as e:
            logging.error("Error on TMDB request - {}".format(e.response))
            time.sleep(10) 
'''

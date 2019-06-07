import logging
import re
import time

import tmdbsimple as tmdb
from requests import HTTPError
from tinydb import Query, operations

from repository import repository
from services.RateLimitedDecorator import RateLimited

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
def search_serie_id(title):
    logging.debug("Searching series with title: {}".format(title))
    try:
        return tmdb.Search().tv(query=title, language='pt-BR')['results'][0]['id']
    except IndexError:
        logging.error("No result found for query(series title: {}".format(title))
        return None


@RateLimited(4)
def serie_info(series_id):
    if series_id:
        return tmdb.TV(series_id).info(language='pt-BR')


@RateLimited(4)
def movie_info(movie_id):
    if movie_id:
        return tmdb.Movies(id=movie_id).info(language='pt-BR')


@RateLimited(4)
def season_info(series_id, season):
    if series_id:
        return tmdb.TV_Seasons(series_id=series_id, season_number=season).info(language='pt-BR')


@RateLimited(4)
def episode_info(series_id, season, episode):
    if series_id:
        return tmdb.TV_Episodes(series_id=series_id, season_number=season, episode_number=episode) \
            .info(language='pt-BR')


def fill_movie_data():
    movies = repository.movies()
    no_data_movies = repository.no_data_movies()

    not_processed_movies = movies.search(Query().movie_data_id == 'NOT_PROCESSED')
    logging.debug("List for movie fill process: {}".format(not_processed_movies))
    for movie in not_processed_movies:
        title = movie['tvg_name']
        title, year = find_year_in_title(title)
        try:
            movie_id = searchMovie(clean_movie_title(title), year)
            movie_data = movie_info(movie_id)
            if movie_data:
                movie_data_id = repository.movie_data().upsert(movie_data, Query().id == movie_id)
                movies.update(operations.set('movie_data_id', movie_data_id[0]), doc_ids=[movie.doc_id])
            else:
                logging.error("No results found for: {}".format(movie['tvg_name']))
                movie['movie_data_id'] = 'NO_DATA_FOUND'
                no_data_movies.upsert(movie, Query().tvg_name == movie['tvg_name'])
                movies.update(operations.set('movie_data_id', 'NO_DATA_FOUND'), doc_ids=[movie.doc_id])
        except HTTPError as e:
            logging.error(
                "Error on TMDB request - {} - Skipping for tvg_name: {}".format(e.response, movie['tvg_name']))
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


def map_to_series_id_dict(title):
    serie_id = search_serie_id(title.strip())
    if serie_id:
        doc_ids = list(map(lambda serie: serie.doc_id, repository.series().search(Query().title == title)))
        return {serie_id: doc_ids}
    else:
        return None


def fill_series_data():
    series = repository.series()
    not_processed_series = series.search(Query().data_id == 'NO_DATA')

    titles = set(list(map(lambda serie: serie['title'], not_processed_series)))
    logging.info("{} series found without data. Filling data".format(len(titles)))

    series_id_dict = dict()
    for title in titles:
        series_id_dict.update(map_to_series_id_dict(title))
    for serie_id in series_id_dict.keys():
        try:
            serie_data = serie_info(serie_id)
            seasons = []
            for season in range(1, int(serie_data['number_of_seasons']) + 1):
                seasons.append(season_info(serie_data['id'], season))
            serie = {
                'id': serie_data['id'],
                'name': serie_data['name'],
                'generos': list(map(lambda genre: genre['name'], serie_data['genres'])),
                'original_title': serie_data['original_name'],
                'overview': serie_data['overview'],
                'poster_path': serie_data['poster_path'],
                'vote_average': serie_data['vote_average'],
                'seasons': seasons
            }
            data_id = repository.series_data().insert(serie)
            repository.series().update(operations.set('data_id', data_id), doc_ids=series_id_dict.get(serie_id))
        except IndexError:
            logging.error("No results found for: {}".format(serie['tvg_name']))
            repository.series().update(operations.set('data_id', 'NO_DATA_FOUND'), doc_ids=series_id_dict.get(serie_id))
        except HTTPError as e:
            logging.error("Error on TMDB request - {}".format(e.response))
            time.sleep(10)

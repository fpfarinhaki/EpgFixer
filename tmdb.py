import logging
import re
import time

import tmdbsimple as tmdb
from requests import HTTPError
from tinydb import Query, where, operations

import Repository
from M3uPatterns import *
from RateLimitedDecorator import RateLimited
from exceptions import *

WRONG_COLECAO_BEGINNING_OF_MOVIE_TITLE = "Coleção.*:\s*"
TITLE_ENDING_UNNECESSARY_NUMBER_ONE = "\s*1$"
tmdb.API_KEY = 'edc5f123313769de83a71e157758030b'

db = Repository.getdb()
movies = db.table('MOVIES')
m3u_movies = db.table('M3U_MOVIES')
no_data_movies = db.table('MOVIES_NO_DATA')


@RateLimited(2)
def searchMovie(name, year):
    filme_id = tmdb.Search().movie(query=name, language='pt-BR', year=year)['results'][0]['id']
    return tmdb.Movies(id=filme_id).info(language='pt-BR')


def update_vod_movies(m3uLine, vodLink):
    if re.match("#EXTINF", m3uLine):
        match = re.search(TVG_NAME_PATTERN, m3uLine)
        tvg_name = match.group(1)
        tvg_group = re.search(GROUP_TITLE_PATTERN, m3uLine).group(1)
        search_by_tvg_name = Query().tvg_name == tvg_name
        if not (m3u_movies.contains(search_by_tvg_name)):
            logging.debug("no movie with tvg-name: {} - insert".format(tvg_name))
            m3u_movies.insert({'tvg_name': tvg_name, 'tvg_group': tvg_group,
                               'vod_link': vodLink, 'movie_id': 'NOT_PROCESSED'})
    else:
        raise NotM3uLine("Argument provided is not a M3U line")


def fill_movie_data():
    not_processed_movies = m3u_movies.search(where('movie_id') == 'NOT_PROCESSED')
    logging.debug("List for movie fill process: {}".format(not_processed_movies))
    for m3uMovie in not_processed_movies:
        title = m3uMovie['tvg_name']
        title, year = find_year_in_title(title)
        # TODO: Spell check movie name
        try:
            movie_id = movies.insert(searchMovie(clean_movie_title(title), year))
            m3u_movies.update(operations.set('movie_id', movie_id), doc_ids=[m3uMovie.doc_id])
        except IndexError:
            logging.error("No results found for: {}".format(m3uMovie['tvg_name']))
            no_data_movies.insert(m3uMovie)
            m3u_movies.update(operations.set('movie_id', 'NO_DATA_FOUND'), doc_ids=[m3uMovie.doc_id])
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

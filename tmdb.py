import logging
import re
from logging.handlers import TimedRotatingFileHandler

import tmdbsimple as tmdb
from RateLimitedDecorator import RateLimited
from M3uPatterns import *
from exceptions import *

WRONG_COLECAO_BEGINNING_OF_MOVIE_TITLE = "Coleção.*:\s*"
TITLE_ENDING_UNNECESSARY_NUMBER_ONE = "\s*1$"
TITLE_RELEASE_YEAR_PATTERN = "\s+([0-9]{4})$"
tmdb.API_KEY = 'edc5f123313769de83a71e157758030b'

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    handlers=[TimedRotatingFileHandler(filename='tmdb.log', encoding='utf-8')])


@RateLimited(3)
def searchMovie(name, year):
    return tmdb.Search().movie(query=name, language='pt-BR', year=year)


def fill_movie_description_m3u(m3uLine):
    if re.match("#EXTINF", m3uLine):
        name, year = '', ''
        m = re.search(TVG_NAME_PATTERN, m3uLine)
        name = m.group(1)
        # Find year of movie and remove from query
        m = re.search(TITLE_RELEASE_YEAR_PATTERN, name)
        if m:
            year = m.group(1)
            name = re.sub(TITLE_RELEASE_YEAR_PATTERN, '', name)
        # Remove number 1 from first movie of trilogy
        name = re.sub(TITLE_ENDING_UNNECESSARY_NUMBER_ONE, '', name)
        # Remove wrong beginning of movie name
        name = re.sub(WRONG_COLECAO_BEGINNING_OF_MOVIE_TITLE, '', name)
        # Remove wrong end of movie name
        # name = re.sub(":\s.*$", '', name)
        name = re.sub("\s\(.*\)$", '', name)
        name = re.sub("\s+-.*", '', name)
        # TODO: Spell check movie name
        movie_results = searchMovie(name, year)
        try:
            filme = movie_results['results'][0]
            sinopse = filme['overview']
            rating = str(filme['vote_average'])
            data_lancamento = str(filme['release_date'])
            insertion_point = re.search("tvg-logo=", m3uLine).start()
            linewithdesc = m3uLine[:insertion_point] \
                           + 'description="{Sinopse:} %s\\n{Nota:} %s\\n{Data de Lançamento:} %s"' % (
                               sinopse, rating, data_lancamento) \
                           + " " + m3uLine[insertion_point:]
            logging.debug(linewithdesc)
            return linewithdesc
        except IndexError:
            logging.error("No results found for: {}".format(name))
            raise NotFound("No results found for: {}".format(name))
    else:
        return m3uLine

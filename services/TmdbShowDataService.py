import logging
import time

import tmdbsimple as tmdb
from requests import HTTPError

from services.RateLimitedDecorator import RateLimited
from services.ShowDataService import ShowDataService


class TmdbShowDataService(ShowDataService):

    def __init__(self) -> None:
        super().__init__()

    tmdb.API_KEY = 'edc5f123313769de83a71e157758030b'

    @RateLimited(4)
    def search_movie_id(self, name, year=''):
        try:
            return tmdb.Search().movie(query=name, language='pt-BR', year=year)['results'][0]['id']
        except HTTPError as e:
            self.handle_http_error(e)
        except IndexError:
            logging.info("No movie found for query=(name = {}, year = {})".format(name, year))
            return None

    @RateLimited(4)
    def search_serie_id(self, title):
        logging.debug("Searching series with title: {}".format(title))
        try:
            return tmdb.Search().tv(query=title, language='pt-BR')['results'][0]['id']
        except HTTPError as e:
            self.handle_http_error(e)
        except IndexError:
            logging.info("No movie found for query=(title = {})".format(title))
            return None

    @RateLimited(4)
    def serie_info(self, series_id):
        if series_id:
            try:
                return tmdb.TV(series_id).info(language='pt-BR')
            except HTTPError as e:
                self.handle_http_error(e)

    @RateLimited(4)
    def movie_info(self, movie_id):
        if movie_id:
            try:
                return tmdb.Movies(id=movie_id).info(language='pt-BR')
            except HTTPError as e:
                self.handle_http_error(e)

    @RateLimited(4)
    def season_info(self, series_id, season):
        if series_id:
            try:
                return tmdb.TV_Seasons(series_id=series_id, season_number=season).info(language='pt-BR')
            except HTTPError as e:
                self.handle_http_error(e)

    def handle_http_error(self, e):
        sleep_time = 10
        logging.error("Error on TMDB request - {}".format(e))
        if e.errno == 429:
            logging.error("Error Request limit exceeded on TMDB - {} - . Sleeping for {} seconds"
                          .format(e, sleep_time))
            time.sleep(sleep_time)

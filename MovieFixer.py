import logging
import re
from logging.handlers import TimedRotatingFileHandler

from tinydb import Query
from tinydb.operations import *

import repository
import tmdb

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    handlers=[TimedRotatingFileHandler(filename='MOVIE_FIXER.log', encoding='utf-8'),
                              logging.StreamHandler()], level=logging.INFO)


class MovieFixer:

    def fix_no_data_movies(self):
        movies = filter(lambda m: m.movie_data_id != 'FIXED', repository.no_data_movies().all())
        for movie in movies:
            movie_name = movie['tvg_name']
            movie_data = self.apply_fixes(movie_name)
            self.update_db(movie_data, movie_name)

    def assign_data_to_movie_manually(self, tvg_name, query):
        logging.info("Manually searching for movie - {} - with query: {}".format(tvg_name, query))
        movie_data = self.get_movie_info(query)

        logging.info("Movie data found - Updating DB")
        logging.debug("Movie data found - {}".format(movie_data))
        self.update_db(movie_data, tvg_name)

    def apply_fixes(self, movie_name):
        fixes = [self.movies_with_date_in_title, self.substring_after_colon, self.substring_before_colon]
        for fix in fixes:
            tentative_name = fix(movie_name)
            movie_data = self.get_movie_info(tentative_name)
            if movie_data:
                return movie_data

    def substring_before_colon(self, movie_name):
        before_colon = re.split(':', movie_name)[0]
        logging.debug("Trying with {} - 'substring_before_colon'".format(before_colon))
        return before_colon

    def substring_after_colon(self, movie_name):
        names = re.split(':', movie_name)
        after_colon = names[len(names) - 1]
        logging.debug("Trying with {} - 'substring_after_colon'".format(after_colon))
        return after_colon

    def movies_with_date_in_title(self, movie_name):
        return movie_name

    def get_movie_info(self, movie_name):
        return tmdb.movie_info(tmdb.searchMovie(movie_name))

    def update_db(self, movie_data, tvg_name):
        movie_data_id = repository.movie_data().upsert(movie_data, Query().id == movie_data['id'])
        repository.movies().update(set('movie_data_id', movie_data_id), Query().tvg_name == tvg_name)
        repository.no_data_movies().update(set('movie_data_id', 'FIXED'), Query().tvg_name == tvg_name)

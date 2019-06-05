import logging
import re

from tinydb import Query
from tinydb.operations import *

from repository import repository
from services import tmdb


class MovieFixer:

    def fix_no_data_movies(self):
        movies = filter(lambda m: m['movie_data_id'] == 'NO_DATA_FOUND', repository.no_data_movies().all())
        for movie in movies:
            logging.info("Trying to apply fix for movies without data - {}".format(movie))
            movie_name = movie['tvg_name']
            movie_data = self.apply_fixes(movie_name)
            self.update_db(movie_data, movie_name)

    def assign_data_to_movie_manually(self, tvg_name, query):
        logging.info("Manually searching for movie - {} - with query: {}".format(tvg_name, query))
        if repository.movies().contains(Query().tvg_name == tvg_name):
            movie_data = self.get_movie_info(query)
            self.update_db(movie_data, tvg_name)
        else:
            logging.info("TVG_NAME provided not part of collection. Skipping")

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
        status = 'MANUAL_FIX_NEEDED'
        try:
            if movie_data:
                logging.info("Movie data found - Updating DB")
                logging.debug("Movie data found - {}".format(movie_data))
                if not (repository.movie_data().contains(Query().id == movie_data['id'])):
                    status = 'FIXED'
                    movie_data_id = repository.movie_data().insert(movie_data)
                    repository.movies().update(set('movie_data_id', movie_data_id), Query().tvg_name == tvg_name)
                else:
                    logging.info("Duplicate movie data. Check logs.")
                    logging.debug("Movie data already in database - {} Check for duplicates and consider manual fixing."
                                  .format("id: " + movie_data['id'] + " title: " + movie_data['title']))
            else:
                logging.info("Movie data not found - Setting as manual fix needed.")
            repository.no_data_movies().update(set('movie_data_id', status), Query().tvg_name == tvg_name)
        except Exception:
            logging.error("Error updating movie during fix.")

    def search_manual_fix_required(self):
        return map(lambda manFix: 'tvg_name: {}\n'.format(manFix['tvg_name']),
                   filter(lambda m: m['movie_data_id'] == 'MANUAL_FIX_NEEDED', repository.no_data_movies().all()))

    def search_shows_with_no_data(self):
        return map(lambda manFix: 'tvg_name: {}'.format(manFix['tvg_name']),
                   filter(lambda m: m['movie_data_id'] == 'NO_DATA_FOUND', repository.no_data_movies().all()))

import logging
import re

from tinydb import Query
from tinydb.operations import *

import repository
import tmdb


class MovieFixer:

    def fix_no_data_movies(self):
        movies = filter(lambda m: m['movie_data_id'] == 'NO_DATA_FOUND', repository.no_data_movies().all())
        for movie in movies:
            logging.info("Trying to apply fix for movies without data - {}".format(movie))
            movie_name = movie['tvg_name']
            movie_data = self.apply_fixes(movie_name)
            self.update_db(movie_data, movie_name)
        with open("movies_need_manual_fix.txt", "w+", encoding='utf8') as need_fix:
            need_fix.write("Movies which need manual fix intervention\n{}".format('-' * 50 + '\n'))
            manual_fix = map(lambda manFix: 'tvg_name: {}\n'.format(manFix['tvg_name']),
                             filter(lambda m: m['movie_data_id'] == 'MANUAL_FIX_NEEDED', repository.no_data_movies().all()))
            need_fix.writelines(manual_fix)

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
        try:
            if movie_data:
                logging.info("Movie data found - Updating DB")
                logging.debug("Movie data found - {}".format(movie_data))
                movie_data_id = repository.movie_data().upsert(movie_data, Query().id == movie_data['id'])
                repository.movies().update(set('movie_data_id', movie_data_id[0]), Query().tvg_name == tvg_name)
                repository.no_data_movies().update(set('movie_data_id', 'FIXED'), Query().tvg_name == tvg_name)
            else:
                logging.info("Movie data not found - Setting as manual fix needed.")
                repository.no_data_movies().update(
                    set('movie_data_id', 'MANUAL_FIX_NEEDED'), Query().tvg_name == tvg_name)
        except Exception:
            logging.error("Error updating movie during fix.")

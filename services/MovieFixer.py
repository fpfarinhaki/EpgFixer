import logging
import re

from tinydb import Query, operations
from tinydb.operations import *

from repository import repository
from services import TmdbShowDataService, ShowDataService
from services.Fixer import Fixer


class MovieFixer(Fixer):
    WRONG_COLECAO_BEGINNING_OF_MOVIE_TITLE = "Coleção.*:\s*"
    TITLE_ENDING_UNNECESSARY_NUMBER_ONE = "\s*1$"

    def __init__(self, show_data_service: ShowDataService):
        super().__init__(show_data_service)

    def fix_no_data_movies(self):
        movies = filter(lambda m: m['movie_data_id'] == 'NO_DATA_FOUND', repository.movies().all())
        for movie in movies:
            logging.info("Trying to apply fix for movies without data - {}".format(movie))
            movie_name = movie['tvg_name']
            movie_data = self.apply_fixes(movie_name)
            self.update_db(movie_data, movie_name)

    def assign_data_manually(self, tvg_name, query):
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
        return TmdbShowDataService.movie_info(TmdbShowDataService.search_movie_id(movie_name))

    def update_db(self, movie_data, tvg_name):
        try:
            if movie_data:
                logging.info("Movie data found - Updating DB")
                logging.debug("Movie data found - {}".format(movie_data))
                if not (repository.movie_data().contains(Query().id == movie_data['id'])):
                    movie_data_id = repository.movie_data().insert(movie_data)
                    repository.movies().update(set('movie_data_id', movie_data_id), Query().tvg_name == tvg_name)
                else:
                    logging.info("Duplicate movie data. Consider improving query for manual fixing.")
                    logging.debug("Movie data already in database - {} Check for duplicates and consider improving "
                                  "query for manual fixing."
                                  .format("id: " + movie_data['id'] + " title: " + movie_data['title']))
            else:
                logging.info("Movie data not found in data service. Check later for updates.")
        except Exception:
            logging.error("Error updating movie during fix.")

    def search_shows_with_no_data(self):
        return list(map(lambda manFix: 'tvg_name: {}'.format(manFix['tvg_name']),
                        filter(lambda m: m['movie_data_id'] == 'NO_DATA_FOUND', repository.movies().all())))

    def fill_show_data(self, movies):
        logging.info("{} movies found without data. Filling data".format(len(movies)))
        for movie in movies:
            title = movie['tvg_name']
            title, year = self.find_year_in_title(title)
            movie_id = self.show_data_service.search_movie_id(self.clean_movie_title(title), year)
            movie_data = self.show_data_service.movie_info(movie_id)
            if movie_data:
                movie_data_id = repository.movie_data().upsert(movie_data, Query().id == movie_id)
                repository.movies().update(operations.set('movie_data_id', movie_data_id[0]), doc_ids=[movie.doc_id])
            else:
                logging.error("No results found for: {}".format(movie['tvg_name']))
                repository.movies().update(operations.set('movie_data_id', 'NO_DATA_FOUND'), doc_ids=[movie.doc_id])

    def find_year_in_title(self, title):
        year = ''
        pattern_year_in_title = "\s+([0-9]{4})$"
        # Find year of movie and remove from query
        match = re.search(pattern_year_in_title, title)
        if match:
            year = match.group(1)
            title = re.sub(pattern_year_in_title, '', title)
        return title, year

    def clean_movie_title(self, name):
        # Remove number 1 from first movie of trilogy
        cleaned_name = re.sub(self.TITLE_ENDING_UNNECESSARY_NUMBER_ONE, '', name)
        # Remove wrong beginning of movie name
        cleaned_name = re.sub(self.WRONG_COLECAO_BEGINNING_OF_MOVIE_TITLE, '', cleaned_name)
        # Remove wrong end of movie name
        # name = re.sub(":\s.*$", '', name)
        cleaned_name = re.sub("\s\(.*\)$", '', cleaned_name)
        cleaned_name = re.sub("\s+-.*", '', cleaned_name)
        return cleaned_name

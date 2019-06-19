import logging
import re

from tinydb import Query, operations
from tinydb.operations import *

from domain.MissingDataItem import MissingDataItem
from repository import repository
from services import ShowDataService
from services.Fixer import Fixer


class MovieFixer(Fixer):
    WRONG_COLECAO_BEGINNING_OF_MOVIE_TITLE = "Coleção.*:\s*"
    TITLE_ENDING_UNNECESSARY_NUMBER_ONE = "\s*1$"

    def __init__(self, show_data_service: ShowDataService):
        super().__init__(show_data_service)

    def remove_show_by_name(self, name):
        removed_ids = repository.movies().update(operations.set('movie_data_id', 'REMOVED'), Query().tvg_name == name)
        logging.info("Removed {} movies with name = {}".format(len(removed_ids), name))

    def fix_no_data_movies(self):
        movies = filter(lambda m: m['movie_data_id'] == 'NO_DATA_FOUND', repository.movies().all())
        for movie in movies:
            logging.info("Trying to apply fix for movies without data - {}".format(movie))
            movie_name = movie['tvg_name']
            movie_data = self.apply_fixes(movie_name)
            self.update_db(movie_data, movie_name)

    def assign_data_manually(self, name, query):
        logging.info("Manually searching for movie - {} - with query: {}".format(name, query))
        year = ''
        match = re.match("(.*)\s*year=([0-9]{4})", query)
        if match:
            year = match.group(2)
            query = match.group(1)
            logging.debug("Search Movie arguments: query = {} year = {}".format(query, year))
        if repository.movies().contains(Query().tvg_name == name):
            movie_id = self.show_data_service.search_movie_id(query, year)
            if movie_id:
                movie_data = self.show_data_service.movie_info(movie_id)
                self.update_db(movie_data, name)
        else:
            logging.info("Show provided is not part of collection. Skipping")

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
        return

    def update_db(self, movie_data, tvg_name):
        try:
            if movie_data:
                logging.info("Movie data found - Updating DB")
                logging.debug("Movie data found - {}".format(movie_data))
                movie_data_id = repository.movie_data().upsert(movie_data, Query().id == movie_data['id'])
                repository.movies().update(set('movie_data_id', movie_data_id[0]), Query().tvg_name == tvg_name)
            else:
                logging.info("Movie data not found in data service. Check later for updates.")
        except Exception:
            logging.error("Error updating movie during fix.")

    def search_shows_with_no_data(self):
        return list(map(lambda manFix: MissingDataItem(manFix['tvg_name'], manFix['tvg_logo']),
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

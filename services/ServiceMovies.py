import logging
import threading

from tinydb import Query

from helpers import m3uCollectors
from helpers.m3uCollectors import M3uMovieCollector
from io_operations import M3uWriter
from repository import repository
from services import ShowDataService
from services.MovieFixer import MovieFixer
from services.Service import Service


class ServiceMovies(Service):
    def __init__(self, file_writer: M3uWriter, mdb_service: ShowDataService):
        super().__init__(file_writer, mdb_service)

    def save(self, m3u_list):
        logging.info("{} - Processing movie database".format(threading.current_thread().name))
        self.update_m3u_entity(m3uCollectors.collect(m3u_list, M3uMovieCollector()), repository.movies())
        MovieFixer(self.mdb_service).fill_show_data(
            repository.movies().search(Query().movie_data_id == 'NOT_PROCESSED'))
        # MovieFixer().fix_no_data_movies()

        sorted_movies = sorted(repository.movie_data().all(), key=lambda m: m['title'])
        for movie_data in sorted_movies:
            m3umovie = repository.movies().get(Query().movie_data_id == movie_data.doc_id)
            if m3umovie:
                self.file_writer.generate_line(m3u_entity=m3umovie, movie_data=movie_data)

        self.file_writer.generate_list()

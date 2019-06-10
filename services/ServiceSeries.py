import logging
import threading

from tinydb import Query, operations

from helpers import m3uCollectors
from helpers.m3uCollectors import M3uSeriesCollector
from io_operations import M3uWriter
from repository import repository
from services import ShowDataService
from services.SeriesFixer import SeriesFixer
from services.Service import Service


class ServiceSeries(Service):

    def __init__(self, file_writer: M3uWriter, mdb_service: ShowDataService):
        super().__init__(file_writer, mdb_service)

    def save(self, m3u_list):
        logging.info("{} - Processing series database".format(threading.current_thread().name))
        self.update_m3u_entity(m3uCollectors.collect(m3u_list, M3uSeriesCollector()), repository.series())
        SeriesFixer(self.mdb_service).fill_series_data(repository.series().search(Query().data_id == 'NO_DATA'))

        sorted_series = sorted(repository.series_data().all(), key=lambda m: m['name'])

        for series_data in sorted_series:
            m3u_series = repository.series().search(Query().data_id == series_data.doc_id)
            for m3u_serie in m3u_series:
                season, episodio = int(m3u_serie['season']), int(m3u_serie['episode'])
                episode_data = ''
                try:
                    episode_data = series_data['seasons'][season - 1]['episodes'][episodio - 1]
                except IndexError:
                    logging.error("No data found for {}  - doc_id {} - Season {} - Episode {}"
                                  .format(m3u_serie['title'], m3u_serie.doc_id, season, episodio))
                    repository.series().update(operations.set('data_id', 'NO_DATA'), doc_ids=[m3u_serie.doc_id])
                self.file_writer.generate_line(m3u_serie=m3u_serie, series_data=series_data, episode_data=episode_data)

        self.file_writer.generate_list()

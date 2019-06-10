import logging
import threading

from helpers import m3uCollectors
from helpers.m3uCollectors import M3uChannelCollector, M3uRadioCollector, M3uChannel24Collector
from io_operations import M3uWriter
from repository import repository
from services import ShowDataService
from services.Service import Service


class ServiceChannels(Service):
    def __init__(self, file_writer: M3uWriter, mdb_service: ShowDataService):
        super().__init__(file_writer, mdb_service)

    def save(self, m3u_list):
        logging.info("{} - Processing channel database".format(threading.current_thread().name))
        self.update_m3u_entity(m3uCollectors.collect(m3u_list, M3uChannelCollector()), repository.channels())
        self.update_m3u_entity(m3uCollectors.collect(m3u_list, M3uRadioCollector()), repository.channels())
        self.update_m3u_entity(m3uCollectors.collect(m3u_list, M3uChannel24Collector()), repository.channels())

        sorted_channels = sorted(repository.channels().all(), key=lambda m: m['tvg_name'])

        for channel in sorted_channels:
            self.file_writer.generate_line(channel)

        self.file_writer.generate_list()

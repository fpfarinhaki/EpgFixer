import logging
import threading

from tinydb import Query

from helpers import m3uCollectors
from helpers.m3uCollectors import *
from io_operations.M3uWriter import M3uWriter
from repository import repository


def save_movies(m3u_list, data_service):
    logging.info("{} - Processing movie database".format(threading.current_thread().name))
    update_m3u_entity(m3uCollectors.collect(m3u_list, M3uMovieCollector()), repository.movies())
    data_service.fill_movie_data()
    # MovieFixer().fix_no_data_movies()

    sorted_movies = sorted(repository.movie_data().all(), key=lambda m: m['title'])
    writer = M3uWriter("movies.m3u")
    for movie_data in sorted_movies:
        m3umovie = repository.movies().get(Query().movie_data_id == movie_data.doc_id)
        if m3umovie:
            writer.generate_movie_line(m3umovie, movie_data)

    writer.generate_list()


def save_channels(m3u_list, epg_dictionary):
    logging.info("{} - Processing channel database".format(threading.current_thread().name))
    update_m3u_entity(m3uCollectors.collect(m3u_list, M3uChannelCollector(epg_dictionary)), repository.channels())
    update_m3u_entity(m3uCollectors.collect(m3u_list, M3uRadioCollector()), repository.channels())
    update_m3u_entity(m3uCollectors.collect(m3u_list, M3uChannel24Collector()), repository.channels())

    sorted_channels = sorted(repository.channels().all(), key=lambda m: m['tvg_name'])

    writer = M3uWriter("channels.m3u")
    for channel in sorted_channels:
        writer.generate_channel_line(channel)

    writer.generate_list()


def save_series(m3u_list, data_service):
    logging.info("{} - Processing series database".format(threading.current_thread().name))
    update_m3u_entity(m3uCollectors.collect(m3u_list, M3uSeriesCollector()), repository.series())
    data_service.fill_series_data()

    sorted_series = sorted(repository.series_data().all(), key=lambda m: m['name'])
    writer = M3uWriter('series.m3u')

    for series_data in sorted_series:
        m3u_serie = repository.series().get(Query().data_id == series_data.doc_id)
        if m3u_serie:
            writer.generate_series_line(m3u_serie, series_data)

    writer.generate_list()


def update_m3u_entity(m3u_entity_list, db):
    logging.debug("Updating {} with {} M3U Entities".format(db, len(m3u_entity_list)))
    to_insert = []
    for m3uEntity in m3u_entity_list:
        if not (db.contains(Query().tvg_name == m3uEntity.tvg_name)):
            logging.debug("Inserting new M3U entity {} - insert".format(m3uEntity))
            to_insert.append(vars(m3uEntity))
    db.insert_multiple(to_insert)

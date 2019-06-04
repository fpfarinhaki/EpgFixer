import logging
import re
import threading
from concurrent.futures.thread import ThreadPoolExecutor

from tinydb import Query

import repository
import tmdb
from M3uPatterns import *
from M3uWriter import M3uWriter
from MovieFixer import MovieFixer
from domain.M3uEntity import M3uEntity, M3uMovie


class M3uFixer:
    def __init__(self, iptv_filename, channelDictionary):
        self.iptv_filename = iptv_filename
        self.channelDictionary = channelDictionary
        self.adultos = []
        self.movies = []
        self.series = []
        self.others = []
        self.channels = []
        self.workers = []

    def readAllLines(self):
        self.lines = [line.rstrip('\n') for line in open(self.iptv_filename, encoding='utf8')]
        return len(self.lines)

    def fixLines(self):
        self.readAllLines()
        numLine = len(self.lines)
        for n in range(numLine):
            line = self.lines[n]
            if line[0] == "#":
                self.manageLine(n)
        self.save_m3u_entities()

    def save_m3u_entities(self):
        with ThreadPoolExecutor(thread_name_prefix='save_thread') as executor:
            movies_future = executor.submit(self.save_movies)
            channel_future = executor.submit(self.save_channels)
            series_future = executor.submit(self.save_series)
            # executor.submit(self.update_m3u_entity, self.adultos, repository.adult_movies())

            logging.debug("Future result for movie thread - {}".format(movies_future.result()))
            logging.debug("Future result for channels thread - {}".format(channel_future.result()))
            logging.debug("Future result for series thread - {}".format(series_future.result()))

    def save_movies(self):
        logging.info("{} - Processing movie database".format(threading.current_thread().name))
        movies_repo = repository.movies()
        self.update_m3u_entity(self.movies, movies_repo)
        tmdb.fill_movie_data()
        MovieFixer().fix_no_data_movies()

        sorted_movies = sorted(repository.movie_data().all(), key=lambda m: m['title'])
        writer = M3uWriter()
        movies_to_write = []
        for movie_data in sorted_movies:
            m3umovie = movies_repo.get(Query().movie_data_id == movie_data.doc_id)
            if m3umovie:
                movies_to_write.append(writer.generate_movie_line(m3umovie, movie_data))

        logging.info("{} - Creating movies list with {} items.".format(threading.current_thread().name, len(sorted_movies)))

        with open('movies.m3u', 'w+', encoding='utf8') as file:
            writer.initialize_m3u_list(file)
            file.writelines(movies_to_write)
        logging.info("{} - Finished creating movies list".format(threading.current_thread().name))

    def save_channels(self):
        logging.info("{} - Processing channel database".format(threading.current_thread().name))
        self.update_m3u_entity(self.channels, repository.channels())
        self.update_m3u_entity(self.others, repository.other())
        channels = repository.channels().all()
        others = repository.other().all()
        sorted_channels = sorted(channels, key=lambda m: m['tvg_name'])
        sorted_other = sorted(others, key=lambda m: m['tvg_name'])
        writer = M3uWriter()
        channels = []
        for channel in sorted_channels:
            channels.append(writer.generate_channel_line(channel))
        for other in sorted_other:
            channels.append(writer.generate_channel_line(other))
        logging.info("{} - Creating channels list with {} items"
                     .format(threading.current_thread().name, len(sorted_channels)))
        with open('channels.m3u', 'w+', encoding='utf8') as file:
            writer.initialize_m3u_list(file)
            file.writelines(channels)
        logging.info("{} - Finished creating channels list".format(threading.current_thread().name))

    def save_series(self):
        logging.info("{} - Processing series database".format(threading.current_thread().name))
        series_repo = repository.series()
        self.update_m3u_entity(self.series, series_repo)

        series = series_repo.all()
        sorted_series = sorted(series, key=lambda m: m['tvg_name'])
        writer = M3uWriter()
        series = []
        for serie in sorted_series:
            series.append(writer.generate_channel_line(serie))
        logging.info("{} - Creating Series list with {} items"
                         .format(threading.current_thread().name, len(sorted_series)))
        with open('series.m3u', 'w+', encoding='utf8') as file:
            writer.initialize_m3u_list(file)
            file.writelines(series)
        logging.info("{} - Finished creating series list".format(threading.current_thread().name))


    def getPossibleKeyMatches(self, key, matcher):
        testkey = key[0:3].casefold()
        # print(testkey)
        if testkey in matcher.replace(' ', '').casefold():
            return True
        else:
            return False

    def manageLine(self, n):
        keys = list(self.channelDictionary.keys())
        lineInfo = self.lines[n]
        lineLink = self.lines[n + 1]
        if lineInfo != "#EXTM3U":
            m = re.search(GROUP_TITLE_PATTERN, lineInfo)
            group = m.group(1)
            if not (group.startswith("Canais:")):
                if group.__contains__("Adulto"):
                    self.adultos.append(M3uEntity(lineInfo, lineLink))
                elif group.startswith("Filme:") or group.startswith("Coleção: "):
                    self.movies.append(M3uMovie(lineInfo, lineLink))
                elif group.startswith("Série:") or group.startswith("Serie:"):
                    self.series.append(M3uEntity(lineInfo, lineLink))
                else:
                    self.others.append(M3uEntity(lineInfo, lineLink))
            else:
                m = re.search(TVG_NAME_PATTERN, lineInfo)
                name = m.group(1)
                possible_key_matches = [k for k in keys if self.getPossibleKeyMatches(k, name)]
                for key in possible_key_matches:
                    if name in self.channelDictionary.get(key):
                        newline = re.sub(TVG_ID_PATTERN, 'tvg-id="' + key + '"', lineInfo)
                        self.channels.append(M3uEntity(newline, lineLink))

    def update_m3u_entity(self, m3u_entity_list, db):
        logging.info("Updating {} M3U Entities".format(len(m3u_entity_list)))
        to_insert = []
        for m3uEntity in m3u_entity_list:
            if not (db.contains(Query().tvg_name == m3uEntity.tvg_name)):
                logging.debug("Inserting new M3U entity {} - insert".format(m3uEntity))
                to_insert.append(vars(m3uEntity))
        db.insert_multiple(to_insert)

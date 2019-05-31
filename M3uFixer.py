import logging
import re
import threading
from concurrent.futures.thread import ThreadPoolExecutor

from tinydb import Query, where

import repository
import tmdb
from M3uPatterns import *
from M3uWriter import M3uWriter
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
            executor.submit(self.save_movies)
            executor.submit(self.save_channels)
            executor.submit(self.save_series)
            # executor.submit(self.update_m3u_entity, self.adultos, repository.adult_movies())
            # executor.submit(self.update_m3u_entity, self.others, repository.other())

    def save_movies(self):
        movies_repo = repository.movies()
        self.update_m3u_entity(self.movies, movies_repo)
        tmdb.fill_movie_data()

        movie_data = repository.movie_data().all()
        sorted_movies = sorted(movie_data, key=lambda m: m['title'])
        writer = M3uWriter()
        with open('movies.m3u', 'w+', encoding='utf8') as file:
            logging.info("{} - Creating movies list with {} items."
                         .format(threading.current_thread().name, len(sorted_movies)))
            writer.initialize_m3u_list(file)
            for movie_data in sorted_movies:
                m3umovie = movies_repo.get(Query().movie_data_id == movie_data.doc_id)
                file.write(writer.generate_movie_line(m3umovie, movie_data))

    def save_channels(self):
        self.update_m3u_entity(self.channels, repository.channels())
        channels = repository.channels().all()
        sorted_channels = sorted(channels, key=lambda m: m['tvg_name'])
        writer = M3uWriter()
        with open('channels.m3u', 'w+', encoding='utf8') as file:
            logging.info("{} - Creating channels list with {} items"
                         .format(threading.current_thread().name, len(sorted_channels)))
            writer.initialize_m3u_list(file)
            for channel in sorted_channels:
                file.write(writer.generate_channel_line(channel))

    def save_series(self):
        series_repo = repository.series()
        self.update_m3u_entity(self.series, series_repo)

        series = series_repo.all()
        sorted_series = sorted(series, key=lambda m: m['tvg_name'])
        writer = M3uWriter()
        with open('series.m3u', 'w+', encoding='utf8') as file:
            logging.info("{} - Creating Series list with {} items"
                         .format(threading.current_thread().name, len(sorted_series)))
            writer.initialize_m3u_list(file)
            for serie in sorted_series:
                file.write(writer.generate_channel_line(serie))

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
        for m3uEntity in m3u_entity_list:
            # search_by_tvg_name = Query().tvg_name == m3uEntity.tvg_name
            # if not (db.contains(search_by_tvg_name)):
            logging.info("Inserting new M3U entity {} - insert".format(m3uEntity))
            db.upsert(vars(m3uEntity), where('tvg_name') == m3uEntity.tvg_name)

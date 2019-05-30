import concurrent
import logging
import re
from concurrent.futures import ALL_COMPLETED
from concurrent.futures.thread import ThreadPoolExecutor

from tinydb import Query

import repository
from M3uEntity import M3uEntity
from M3uPatterns import *


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
        futures = []
        executor = ThreadPoolExecutor()
        futures.append(executor.submit(self.update_m3u_entity, self.movies, repository.movies()))
        executor.submit(self.update_m3u_entity, self.channels, repository.channels())
        executor.submit(self.update_m3u_entity, self.series, repository.series())
        executor.submit(self.update_m3u_entity, self.adultos, repository.adult_movies())
        executor.submit(self.update_m3u_entity, self.others, repository.other())
        concurrent.futures.wait(futures, return_when=ALL_COMPLETED)

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
                    self.movies.append(M3uEntity(lineInfo, lineLink))
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
            if re.match("#EXTINF", m3uEntity.line):
                tvg_id = re.search(TVG_ID_PATTERN, m3uEntity.line).group(1)
                tvg_name = re.search(TVG_NAME_PATTERN, m3uEntity.line).group(1)
                tvg_group = re.search(GROUP_TITLE_PATTERN, m3uEntity.line).group(1)
                tvg_logo = re.search(TVG_LOGO_PATTERN, m3uEntity.line).group(1)
                search_by_tvg_name = Query().tvg_name == tvg_name
                if not (db.contains(search_by_tvg_name)):
                    logging.debug("no m3u entity with tvg-name: {} - insert".format(tvg_name))
                    db.insert({'tvg_id': tvg_id, 'tvg_name': tvg_name, 'tvg_group': tvg_group, 'tvg_logo':tvg_logo,
                                     'vod_link': m3uEntity.link, 'movie_id': 'NOT_PROCESSED'})
            else:
                logging.error("Argument provided is not a M3U line - {}".format(m3uEntity.line))

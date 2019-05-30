import logging
import re
import Repository
import tmdb

from tinydb import Query
from tinydb.database import Table
from M3uPatterns import *


class M3uFixer:
    def __init__(self, iptv_filename, channelDictionary, vod_enable_update):
        self.iptv_filename = iptv_filename
        self.channelDictionary = channelDictionary
        self.channels = []
        self.adult_movies = []
        self.bad_movies = []
        self.series = []
        self.vod_update_enabled = vod_enable_update


    def vodUpdateEnabled(self):
        return self.vod_update_enabled.casefold() == "true"

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

        self.save_to_file("channels.m3u", self.channels)
        if self.vodUpdateEnabled():
            tmdb.fill_movie_data()
            self.save_to_file("need_fixes.m3u", self.bad_movies)
            self.save_to_file("adult_movies.m3u", self.adult_movies)
            self.save_to_file("series.m3u", self.series)

    def save_to_file(self, filename, list):
        with open(filename, "w+", encoding='utf8') as file:
            file.write("#EXTM3U\n")
            file.writelines(list)

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
                if self.vodUpdateEnabled():
                    if group.__contains__("Adulto"):
                        self.update_m3u_entity(lineInfo, lineLink, Repository.getdb().table('M3U_MOVIES_ADULT'))
                    elif group.startswith("Filme:") or group.startswith("Coleção: "):
                        self.update_m3u_entity(lineInfo, lineLink, Repository.getdb().table('M3U_MOVIES'))
                    elif group.startswith("Série:") or group.startswith("Serie:"):
                        self.update_m3u_entity(lineInfo, lineLink, Repository.getdb().table('M3U_SERIES'))
                    else:
                        self.update_m3u_entity(lineInfo, lineLink, Repository.getdb().table('M3U_OTHER'))
            else:
                m = re.search(TVG_NAME_PATTERN, lineInfo)
                name = m.group(1)
                possible_key_matches = [k for k in keys if self.getPossibleKeyMatches(k, name)]
                for key in possible_key_matches:
                    if name in self.channelDictionary.get(key):
                        newline = re.sub(TVG_ID_PATTERN, 'tvg-id="' + key + '"', lineInfo)
                        self.update_m3u_entity(lineInfo, lineLink, Repository.getdb().table('M3U_CHANNEL'))
                        self.channels.append(newline + '\n')
                        self.channels.append(lineLink + '\n')

    def update_m3u_entity(self, lineInfo, lineLink, db_table: Table):
        if re.match("#EXTINF", lineInfo):
            match = re.search(TVG_NAME_PATTERN, lineInfo)
            tvg_name = match.group(1)
            tvg_group = re.search(GROUP_TITLE_PATTERN, lineInfo).group(1)
            search_by_tvg_name = Query().tvg_name == tvg_name
            if not (db_table.contains(search_by_tvg_name)):
                logging.debug("no m3u entity with tvg-name: {} - insert".format(tvg_name))
                db_table.insert({'tvg_name': tvg_name, 'tvg_group': tvg_group,
                                 'vod_link': lineLink, 'movie_id': 'NOT_PROCESSED'})
        else:
            logging.error("Argument provided is not a M3U line - {}".format(lineInfo))

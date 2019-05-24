import logging
import re
import tmdb
from M3uPatterns import *
from exceptions import NotFound

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
handler = logging.FileHandler('fixer.log', 'a+', encoding='utf-8')
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', handlers=[handler])


class M3uFixer:

    def __init__(self, iptv_filename, channelDictionary, vod_enable_update):
        self.iptv_filename = iptv_filename
        print(self.iptv_filename)
        self.channelDictionary = channelDictionary
        self.channels = []
        self.movies = []
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
            self.save_to_file("movies.m3u", self.movies)
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
                    logger.debug("VOD update enabled")
                    if group.__contains__("Adulto"):
                        self.adult_movies.append(lineInfo + '\n')
                        self.adult_movies.append(lineLink + '\n')
                    elif group.startswith("Filme:") or group.startswith("Coleção: "):
                        try:
                            filled = tmdb.fill_movie_description_m3u(lineInfo)
                            self.movies.append(filled + '\n')
                            self.movies.append(lineLink + '\n')
                        except NotFound:
                            self.bad_movies.append(lineInfo + '\n')
                            self.bad_movies.append(lineLink + '\n')
                    elif group.startswith("Série:") or group.startswith("Serie:"):
                        self.series.append(lineInfo + '\n')
                        self.series.append(lineLink + '\n')
                    else:
                        self.channels.append(lineInfo + '\n')
                        self.channels.append(lineLink + '\n')
            else:
                m = re.search(TVG_NAME_PATTERN, lineInfo)
                name = m.group(1)
                possible_key_matches = [k for k in keys if self.getPossibleKeyMatches(k, name)]
                for key in possible_key_matches:
                    if name in self.channelDictionary.get(key):
                        newline = re.sub(TVG_ID_PATTERN, 'tvg-id="' + key + '"', lineInfo)
                        self.channels.append(newline + '\n')
                        self.channels.append(lineLink + '\n')


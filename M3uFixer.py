import logging
import re
import time

import tmdbsimple as tmdb

WRONG_COLECAO_BEGINNING_OF_MOVIE_TITLE = "Coleção.*:\s*"
TVG_ID_PATTERN = "tvg-id=\"(.*?)\""
GROUP_TITLE_PATTERN = "group-title=\"(.*?)\""
TVG_NAME_PATTERN = "tvg-name=\"(.*?)\""
TITLE_ENDING_UNNECESSARY_NUMBER_ONE = "\s*1$"
TITLE_RELEASE_YEAR_PATTERN = "\s+([0-9]{4})$"

tmdb.API_KEY = 'edc5f123313769de83a71e157758030b'
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
handler = logging.FileHandler('fixer.log', 'a+', encoding='utf-8')
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', handlers=[handler])


class M3uFixer:

    def __init__(self, iptv_filename, channelDictionary, vod_enable_update):
        self.iptv_filename = iptv_filename
        self.channelDictionary = channelDictionary
        self.channels = []
        self.movies = []
        self.series = []
        self.vod_update_enabled = vod_enable_update

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
        if self.vod_update_enabled:
            self.save_to_file("movies.m3u", self.movies)
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
                if self.vod_update_enabled:
                    if group.startswith("Filme:") or group.startswith("Coleção: "):
                        self.movies.append(self.fill_movie_metadata(lineInfo) + '\n')
                        self.movies.append(lineLink + '\n')
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

    def fill_movie_metadata(self, line):
        if re.match("#EXTINF", line):
            name, year = '', ''
            m = re.search(TVG_NAME_PATTERN, line)
            name = m.group(1)
            # Find year of movie and remove from query
            m = re.search(TITLE_RELEASE_YEAR_PATTERN, name)
            if m:
                year = m.group(1)
                name = re.sub(TITLE_RELEASE_YEAR_PATTERN, '', name)
            # Remove number 1 from first movie of trilogy
            name = re.sub(TITLE_ENDING_UNNECESSARY_NUMBER_ONE, '', name)
            # Remove wrong beginning of movie name
            name = re.sub(WRONG_COLECAO_BEGINNING_OF_MOVIE_TITLE, '', name)
            # Remove wrong end of movie name
            # name = re.sub(":\s.*$", '', name)
            name = re.sub("\s\(.*\)$", '', name)
            name = re.sub("\s+-.*", '', name)
            # TODO: Spell check movie name
            movie_results = tmdb.Search().movie(query=name, language='pt-BR', year=year)
            try:
                filme = movie_results['results'][0]
                sinopse = filme['overview']
                rating = str(filme['vote_average'])
                data_lancamento = str(filme['release_date'])
                linewithdesc = line + " " \
                               + 'description="{Sinopse:} %s\\n{Nota:} %s\\n{Data de Lançamento:} %s\\n"' % (
                                   sinopse, rating, data_lancamento)
                logging.debug(linewithdesc)
                return linewithdesc
            except IndexError:
                logging.error("No results found for: {}".format(name))
                return line
        else:
            return line


def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rateLimitedFunction(*args, **kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.clock()
            return ret

        return rateLimitedFunction

    return decorate

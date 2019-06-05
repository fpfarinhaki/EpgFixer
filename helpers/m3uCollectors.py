from domain.M3uEntity import M3uMovie, M3uEntity


class M3uCollector:
    def collect(self, m3u_entity):
        pass


def collect(m3u_entities, collector: M3uCollector):
    return list(filter(None.__ne__, map(lambda entity: collector.collect(entity), m3u_entities)))


class M3uChannelCollector(M3uCollector):
    def __init__(self, channel_dictionary):
        self.channelDictionary = channel_dictionary

    def collect(self, m3u_entity):
        group = m3u_entity.tvg_group
        if group.__contains__("Canais:") and not (group.__contains__("Adultos")):
            keys = list(self.channelDictionary.keys())
            possible_key_matches = [k for k in keys if self.getPossibleKeyMatches(k, m3u_entity.tvg_name)]
            for key in possible_key_matches:
                if m3u_entity.tvg_name in self.channelDictionary.get(key):
                    m3u_entity.tvg_id = key
                    return m3u_entity

    def getPossibleKeyMatches(self, key, matcher):
        if key[0:3].casefold() in matcher.replace(' ', '').casefold():
            return True
        else:
            return False


class M3uMovieCollector(M3uCollector):
    def collect(self, m3u_entity):
        group = m3u_entity.tvg_group
        if (group.__contains__("Filme:") or group.__contains__("Coleção: ")) and not (group.__contains__("Adultos")):
            return M3uMovie(m3u_entity.line, m3u_entity.link)


class M3uSeriesCollector(M3uCollector):
    def collect(self, m3u_entity):
        group = m3u_entity.tvg_group
        if group.__contains__("Série:") or group.__contains__("Serie:"):
            return M3uEntity(m3u_entity.line, m3u_entity.link)


class M3uRadioCollector(M3uCollector):
    def collect(self, m3u_entity):
        group = m3u_entity.tvg_group
        if group.__contains__("Rádios") or group.__contains__("Radios:"):
            return M3uEntity(m3u_entity.line, m3u_entity.link)


class M3uAdultCollector(M3uCollector):
    def collect(self, m3u_entity):
        group = m3u_entity.tvg_group
        if group.__contains__("Adultos"):
            if group.__contains__("Filme:"):
                return M3uMovie(m3u_entity.line, m3u_entity.link)
            else:
                return M3uEntity(m3u_entity.line, m3u_entity.link)


class M3uChannel24Collector(M3uCollector):
    def collect(self, m3u_entity):
        group = m3u_entity.tvg_group
        if group.__contains__("Canais: 24") and not (group.__contains__("Adultos")):
            return m3u_entity

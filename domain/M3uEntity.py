import re

TVG_ID_PATTERN = "tvg-id=\"(.*?)\""
GROUP_TITLE_PATTERN = "group-title=\"(.*?)\""
TVG_NAME_PATTERN = "tvg-name=\"(.*?)\""
TVG_LOGO_PATTERN = "tvg-logo=\"(.*?)\""


class M3uEntity(object):
    def __init__(self, line, link):
        self.line = line
        self.tvg_id = re.search(TVG_ID_PATTERN, line).group(1)
        self.tvg_name = re.search(TVG_NAME_PATTERN, line).group(1)
        self.tvg_group = re.search(GROUP_TITLE_PATTERN, line).group(1)
        self.tvg_logo = re.search(TVG_LOGO_PATTERN, line).group(1)
        self.link = link

    def __repr__(self) -> str:
        return 'TVG-NAME {} - LINK {}'.format(self.tvg_name, self.link)


class M3uMovie(M3uEntity):
    def __init__(self, line, link, movie_data_id='NOT_PROCESSED'):
        M3uEntity.__init__(self, line, link)
        self.movie_data_id = movie_data_id


class M3uSerie(M3uEntity):

    def __init__(self, line, link, data_id='NO_DATA'):
        M3uEntity.__init__(self, line, link)
        self.data_id = data_id
        self.season = '01'
        self.episode = '01'

    def assign_season_and_episode(self):
        match = re.search("S([0-9]{1,2})\s*E([0-9]{1,3})\s*$", self.tvg_name)
        if match:
            self.season = match.group(1)
            self.episode = match.group(2)

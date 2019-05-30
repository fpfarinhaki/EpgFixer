import logging

from datetime import *
from string import Template

description_template = Template('description="{Título:} $title\\n'
                                '{Gênero:} $genre\\n'
                                '{Sinopse:} $overview\\n'
                                '{Nota:} $vote_average\\n'
                                '{Data de Lançamento:} $release_date"')

line_template = ('#EXTINF:-1 tvg-id="{id}" '
                 'tvg-name="{title}" {description} tvg-logo="http://image.tmdb.org/t/p/w300{poster_path}" '
                 'group-title="{tvg_group}",{title}\n'
                 '{vod_link}\n')


class M3uWriter:
    def initialize_m3u_list(self, file):
        file.write("#EXTM3U\n")
        return file

    def generate_movie_line(self, m3uMovie, tmdb_data):
        description = description_template.safe_substitute(tmdb_data,
                   genre=', '.join(map(lambda genre: genre['name'], tmdb_data['genres'])),
                   release_date=datetime.strftime(datetime.strptime(tmdb_data['release_date'], '%Y-%m-%d'), '%d-%m-%Y'))
        filled_line = line_template.format(**m3uMovie, **tmdb_data, description=description)
        logging.debug(filled_line)
        return filled_line

import logging

from datetime import *
from string import Template

movie_description_template = Template('description="{Título Original:} $original_title\\n'
                                '{Data de Lançamento:} $release_date\\n'
                                '\\n{Sinopse:} $overview\\n'
                                '\\n$genre\\t\\t $runtime min.'
                                '{Avaliação:} $vote_average\\n"')

series_description_template = Template('description="{Título Original:} $original_title\\n'
                                      '{Gênero:} $genre'
                                      '{Temporada:} $season {Episódio:} $episode\\n'
                                      '{Data de Lançamento:} $release_date\\n'
                                      '\\n{Sinopse:} $overview\\n'
                                      '\\n{Duração} $runtime min.\\t{Avaliação:} $vote_average"')

line_with_description_template = ('#EXTINF:-1 tvg-id="{id}" '
                       'tvg-name="{title}" {description} tvg-logo="http://image.tmdb.org/t/p/w400{poster_path}" '
                       'group-title="{tvg_group}",{title}\n'
                       '{vod_link}\n')

channel_line_template = ('#EXTINF:-1 tvg-id="{tvg_id}" '
                         'tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" '
                         'group-title="{tvg_group}",{tvg_name}\n'
                         '{vod_link}\n')


class M3uWriter:
    def initialize_m3u_list(self, file):
        file.write("#EXTM3U\n")
        return file

    def generate_movie_line(self, m3uMovie, movie_data):
        try:
            release_date = datetime.strftime(datetime.strptime(movie_data['release_date'], '%Y-%m-%d'), '%d-%m-%Y')
        except ValueError:
            logging.error("Release date not in proper format - {} - tvg_name: {}".format(movie_data['release_date'], m3uMovie['tvg_name']))
            release_date = movie_data['release_date']
        description = movie_description_template.safe_substitute(movie_data,
                 genre=', '.join(map(lambda genre: genre['name'], movie_data['genres'])), release_date=release_date)
        filled_line = line_with_description_template.format(**m3uMovie, **movie_data, description=description)
        logging.debug(filled_line)
        return filled_line

    def generate_channel_line(self, channel):
        return channel_line_template.format(**channel, doc_id=channel.doc_id)

    def generate_series_line(self, m3uSerie, series_data):
        try:
            release_date = datetime.strftime(datetime.strptime(series_data['release_date'], '%Y-%m-%d'), '%d-%m-%Y')
        except ValueError:
            logging.error("Release date not in proper format - {} - tvg_name: {}".format(series_data['release_date'], m3uSerie['tvg_name']))
            release_date = series_data['release_date']

        #description = series_description_template.safe_substitute(series_data, genre=', '.join(map(lambda genre: genre['name'], series_data['genres'])), release_date=release_date)
        filled_line = line_with_description_template.format(**m3uSerie, **series_data, description='')
        logging.debug("Series line generatede: {}".format(filled_line))
        return filled_line
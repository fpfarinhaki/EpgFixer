import logging
import threading

from datetime import *
from string import Template

LINE_WITH_DESCRIPTION_TEMPLATE = ('#EXTINF:-1 tvg-id="{id}" '
                                  'tvg-name="{tvg_name}" {description} tvg-logo="http://image.tmdb.org/t/p/w400{poster_path}" '
                                  'group-title="{tvg_group}",{title}\n'
                                  '{link}\n')

DEFAULT_M3U_LINE = ('#EXTINF:-1 tvg-id="{tvg_id}" '
                    'tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" '
                    'group-title="{tvg_group}",{tvg_name}\n'
                    '{link}\n')


class M3uWriter:

    def __init__(self, filename):
        self.buffer = []
        self.filename = filename

    def generate_list(self):
        logging.info("{} - Creating list {} with {} items"
                     .format(threading.current_thread().name, self.filename, len(self.buffer)))
        with open(self.filename, 'w+', encoding='utf8') as file:
            file.write("#EXTM3U\n")
            file.writelines(self.buffer)
        logging.info("{} - Finished creating list {}".format(threading.current_thread().name, self.filename))

    def generate_movie_line(self, m3uMovie, movie_data):
        description = Template('description="{Título Original:} $original_title\\n'
                               '{Data de Lançamento:} $release_date\\n'
                               '\\n{Sinopse:} $overview\\n'
                               '\\n$genre\\t\\t $runtime min.\\n'
                               '{Avaliação:} $vote_average"') \
            .safe_substitute(movie_data,
                             genre=', '.join(map(lambda genre: genre['name'], movie_data['genres'])),
                             release_date=format_release_date(movie_data['release_date']))

        self.buffer.append(fill_line_with_description(description, m3uMovie, movie_data))

    def generate_series_line(self, m3uSerie, series_data):
        season, episodio = int(m3uSerie['season']), int(m3uSerie['episode'])
        try:
            episode_data = series_data['seasons'][season - 1]['episodes'][episodio - 1]
            description = Template('description="{Episódio: } $name\\n'
                                   '{Temporada:} $season {Episódio:} $episode\\n'
                                   '{Data de Estréia:} $estreia\\n'
                                   '\\n{Sinopse:} $overview\\n'
                                   '\\n{Avaliação:} $vote_average"') \
                .safe_substitute(episode_data, estreia=format_release_date(episode_data['air_date']),
                                 season=season, episode=episodio)
        except IndexError:
            description = ''
            logging.error("Episode details not found for serie {} - Season {} - Episode {}"
                          .format(m3uSerie.title, season, episodio))

        self.buffer.append(fill_line_with_description(description=description, m3uEntity=m3uSerie,
                                                      show_data=series_data))

    def generate_channel_line(self, channel):
        self.buffer.append(DEFAULT_M3U_LINE.format(**channel, doc_id=channel.doc_id))


def fill_line_with_description(description, m3uEntity, show_data):
    filled_line = LINE_WITH_DESCRIPTION_TEMPLATE.format(**m3uEntity, **show_data, description=description)
    logging.debug("Line generated: {}".format(filled_line))
    return filled_line


def format_release_date(date):
    try:
        release_date = datetime.strftime(datetime.strptime(date, '%Y-%m-%d'), '%d-%m-%Y')
    except ValueError:
        logging.error("Release date not in proper format - {}".format(date))
        release_date = date

    return release_date

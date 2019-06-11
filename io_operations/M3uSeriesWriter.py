from string import Template

from io_operations.M3uWriter import M3uWriter
from utils.dateutils import format_release_date


class M3uSeriesWriter(M3uWriter):
    SERIES_LINE_WITH_DESCRIPTION_TEMPLATE = ('#EXTINF:-1 tvg-id="" '
                                             'tvg-name="{tvg_name}" {description} tvg-logo="http://image.tmdb.org/t/p/w400{poster_path}" '
                                             'group-title="{tvg_group}",{title} S{season} E{episode}\n'
                                             '{link}\n')

    SERIES_LINE_INFORMATION_TEMPLATE = ('#EXTINF:-1 tvg-id="" '
                                        'tvg-name="{name}" {description} tvg-logo="http://image.tmdb.org/t/p/w400{poster_path}" '
                                        'group-title="{tvg_group}",{name}\n'
                                        'http://sample.serie.tv/description\n')

    def __init__(self, filename):
        super().__init__(filename)
        self.series_line_dict = {}

    def generate_line(self, m3u_serie, series_data, episode_data):
        name_key = series_data['name']
        if name_key in self.series_line_dict:
            self.buffer.append(self.generate_episode_line(episode_data, m3u_serie, series_data))
        else:
            self.series_line_dict[name_key] = []
            self.buffer.append(self.generate_information_line(m3u_serie, series_data))
            self.buffer.append(self.generate_episode_line(episode_data, m3u_serie, series_data))

    def generate_episode_line(self, episode_data, m3u_serie, series_data):
        if episode_data:
            description = Template('description="{Episódio:} $name\\n'
                                   '{Temporada:} $season_number {Episódio:} $episode_number\\n'
                                   '{Data de Estréia:} $estreia\\n'
                                   '\\n{Sinopse:} $overview\\n'
                                   '\\n{Avaliação:} $vote_average"') \
                .safe_substitute(episode_data, estreia=format_release_date(episode_data['air_date']))
        else:
            description = ''

        return self.SERIES_LINE_WITH_DESCRIPTION_TEMPLATE.format(**m3u_serie, **series_data, description=description)

    def generate_information_line(self, m3u_serie, series_data):
        description = Template('description="{Título:} $name {Título Original:} $original_title\\n'
                               '{Genero:} $generos\\n'
                               '{Temporadas:} $seasons_number\\n'
                               '\\n{Sinopse:} $overview\\n'
                               '\\n{Avaliação:} $vote_average"') \
            .safe_substitute(**series_data, seasons_number=len(series_data['seasons']))

        return self.SERIES_LINE_INFORMATION_TEMPLATE.format(**m3u_serie, **series_data, description=description)

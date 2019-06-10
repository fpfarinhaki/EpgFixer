from string import Template

from io_operations.M3uWriter import M3uWriter
from utils.dateutils import format_release_date


class M3uSeriesWriter(M3uWriter):
    SERIES_LINE_WITH_DESCRIPTION_TEMPLATE = ('#EXTINF:-1 tvg-id="" '
                                             'tvg-name="{tvg_name}" {description} tvg-logo="http://image.tmdb.org/t/p/w400{poster_path}" '
                                             'group-title="{tvg_group}",{title} S{season} E{episode}\n'
                                             '{link}\n')

    def __init__(self, filename):
        super().__init__(filename)

    def generate_line(self, m3u_serie, series_data, episode_data):
        if episode_data:
            description = Template('description="{Episódio:} $name\\n'
                                   '{Temporada:} $season_number {Episódio:} $episode_number\\n'
                                   '{Data de Estréia:} $estreia\\n'
                                   '\\n{Sinopse:} $overview\\n'
                                   '\\n{Avaliação:} $vote_average"') \
                .safe_substitute(episode_data, estreia=format_release_date(episode_data['air_date']))
        else:
            description = ''

        self.buffer.append(
            self.SERIES_LINE_WITH_DESCRIPTION_TEMPLATE.format(**m3u_serie, **series_data, description=description))

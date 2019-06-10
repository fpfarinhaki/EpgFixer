from string import Template

from io_operations.M3uWriter import M3uWriter
from utils.dateutils import format_release_date


class M3uMoviesWriter(M3uWriter):
    MOVIE_LINE_WITH_DESCRIPTION_TEMPLATE = ('#EXTINF:-1 tvg-id="" '
                                            'tvg-name="{tvg_name}" {description} tvg-logo="http://image.tmdb.org/t/p/w400{poster_path}" '
                                            'group-title="{tvg_group}",{title}\n'
                                            '{link}\n')

    def __init__(self, filename):
        super().__init__(filename)

    def generate_line(self, m3u_entity, movie_data):
        description = Template('description="{Título Original:} $original_title\\n'
                               '{Data de Lançamento:} $release_date\\n'
                               '\\n{Sinopse:} $overview\\n'
                               '\\n$genre\\t\\t $runtime min.\\n'
                               '{Avaliação:} $vote_average"') \
            .safe_substitute(movie_data, genre=', '.join(map(lambda genre: genre['name'], movie_data['genres'])),
                             release_date=format_release_date(movie_data['release_date']))
        self.buffer.append(
            self.MOVIE_LINE_WITH_DESCRIPTION_TEMPLATE.format(**m3u_entity, **movie_data, description=description))

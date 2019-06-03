import sys

from MovieFixer import MovieFixer

MovieFixer().assign_data_to_movie_manually(tvg_name=sys.argv[1], query=sys.argv[2])

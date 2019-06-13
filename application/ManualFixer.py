"""Manual Movie Fixer CLI
Usage:
    ManualFixer.py (--show-type=<type>) (--fix <name> <query> | --list) [options]

Options:
-h --help                           Show this
--show-type=<type>                  Type of show: movies or series [default: movies]
--fix                               Fix show. Requires arguments name and query
--list                              List names of missing data for type: movies or series
--debug                             Show debug information
--quiet                             Display errors only

"""
import logging
from logging.handlers import TimedRotatingFileHandler

from docopt import docopt

from services.Fixer import Fixer
from services.MovieFixer import MovieFixer
from services.SeriesFixer import SeriesFixer
from services.TmdbShowDataService import TmdbShowDataService

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Manual Movie Fixer 1.0')
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    if arguments['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    elif arguments['--quiet']:
        logging.basicConfig(level=logging.ERROR)
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        handlers=[TimedRotatingFileHandler(filename='ManualDataFixing.log', encoding='utf-8'),
                                  console_handler], level=logging.DEBUG)

    service: Fixer = ''
    mdb_service = TmdbShowDataService()
    if arguments['--show-type'] == 'movies':
        service = MovieFixer(mdb_service)
    elif arguments['--show-type'] == 'series':
        service = SeriesFixer(mdb_service)

    if arguments['--list']:
        print("Shows which need manual fix intervention\n{}".format('-' * 50))
        for show in service.search_shows_with_no_data():
            print("Name: {} - poster_path: {:>15}".format(show.name, show.poster_path))
    else:
        service.assign_data_manually(arguments['<name>'], query=arguments['<query>'])

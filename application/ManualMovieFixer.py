"""Manual Movie Fixer CLI
Usage:
    ManualMovieFixer.py (--list (--series | --movies) | [options] <tvg_name> <query> -o <file>)

Arguments:
    tvg_name    Should match m3ulist tvg_name needing fix. See --list below
    query       Query that will be used to search for movie information.

Options:
-h --help                           show this
-l --list  (--series | --movies)    list all shows needing manual fix
-o <file>, --output <file>          save to file
--debug                             show debug information
--quiet                             display errors only

"""
import logging
from logging.handlers import TimedRotatingFileHandler

from docopt import docopt

from services.MovieFixer import MovieFixer
from services.SeriesFixer import SeriesFixer

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

    if arguments['--list']:
        print("Shows which need manual fix intervention\n{}".format('-' * 50 + '\n'))
        if arguments['--movies']:
            for show in MovieFixer().search_shows_with_no_data():
                print(show)
        elif arguments['--series']:
            for show in SeriesFixer().search_shows_with_no_data():
                print(show)

    else:
        MovieFixer().assign_data_to_movie_manually(tvg_name=arguments['<tvg_name>'], query=arguments['<query>'])

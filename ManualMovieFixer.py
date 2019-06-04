"""Manual Movie Fixer CLI
Usage:
    ManualMovieFixer.py [options] [--list | (<tvg_name> <query>)]

tvg_name    Should match m3ulist tvg_name needing fix. See --list below
query       Query that will be used to search for movie information.

Options:
-h --help   show this
-l --list   list all shows needing manual fix
--debug     show debug information
--quiet     display errors only

"""
import logging
from logging.handlers import TimedRotatingFileHandler

from docopt import docopt

from MovieFixer import MovieFixer

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Manual Movie Fixer 1.0')
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        for show in MovieFixer().search_shows_with_no_data():
            print(show)
    else:
        MovieFixer().assign_data_to_movie_manually(tvg_name=arguments['<tvg_name>'], query=arguments['<query>'])

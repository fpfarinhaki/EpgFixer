"""Manual Movie Fixer CLI
Usage:
    ManualMovieFixer.py [options] <tvg_name> <query>

tvg_name    Should match m3ulist tvg_name. Can be found in file ***_need_manual_fix.txt
query       Query that will be used to search for movie information.

Options:
-h --help   show this
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

    MovieFixer().assign_data_to_movie_manually(tvg_name=arguments['<tvg_name>'], query=arguments['<query>'])

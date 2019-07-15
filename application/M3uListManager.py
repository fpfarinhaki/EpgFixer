"""M3U List Manager CLI
Usage:
    M3uListManager [options] ([--type=<type>] --m3u-file filename | --update-db script)

Options:
-h --help               show this
--type=<type>          (optional) type of list to process: channels, series or movies. Default to all.
--m3u-file <filename>   save to file
--update-db <script>    update db using script provided
--debug                 show debug information
--quiet                 display errors only

"""
import logging
import runpy
from concurrent.futures.thread import ThreadPoolExecutor
from logging.handlers import TimedRotatingFileHandler

from docopt import docopt

from io_operations.M3uChannelsWriter import M3uChannelsWriter
from io_operations.M3uMoviesWriter import M3uMoviesWriter
from io_operations.M3uSeriesWriter import M3uSeriesWriter
from io_operations.M3uTransformer import M3uTransformer
from services.ServiceChannels import ServiceChannels
from services.ServiceMovies import ServiceMovies
from services.ServiceSeries import ServiceSeries
from services.TmdbShowDataService import TmdbShowDataService

console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(message)s')
console_handler.setFormatter(formatter)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    handlers=[TimedRotatingFileHandler(filename='M3U_FIXER.log', encoding='utf-8'),
                              console_handler], level=logging.DEBUG)


def main(iptv_filename, services):
    logging.info("Starting EPG and movie data process.")
    all_m3u = M3uTransformer(iptv_filename).transform()

    with ThreadPoolExecutor(thread_name_prefix='save_thread') as executor:
        for service in services:
            future = executor.submit(service.save, all_m3u)
            logging.debug("Future result for {} thread - {}".format(service.__class__.__name__, future.result()))

    logging.info("M3u process finished.")


if __name__ == '__main__':
    show_data_service = TmdbShowDataService()
    services = [ServiceSeries(M3uSeriesWriter("series.m3u"), show_data_service),
                ServiceMovies(M3uMoviesWriter('movies.m3u'), show_data_service),
                ServiceChannels(M3uChannelsWriter('channels.m3u'), show_data_service)
                ]
    arguments = docopt(__doc__, version='M3U List Manager 1.0')
    console_handler.setLevel(logging.INFO)
    if arguments['--debug']:
        console_handler.setLevel(logging.DEBUG)
    elif arguments['--quiet']:
        console_handler.setLevel(logging.ERROR)

    if arguments['--update-db']:
        runpy.run_path(arguments['--update-db'])
    else:
        if arguments['--type'] == 'channels':
            main(arguments['--m3u-file'], [services.pop(2)])
        elif arguments['--type'] == 'movies':
            main(arguments['--m3u-file'], [services.pop(1)])
        elif arguments['--type'] == 'series':
            main(arguments['--m3u-file'], [services.pop(0)])
        else:
            main(arguments['--m3u-file'], services)

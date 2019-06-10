"""M3U List Manager CLI
Usage:
    M3uListManager [options] (--m3u-file filename | --update-db script)

Options:
-h --help               show this
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


def main(iptv_filename):
    logging.info("Starting EPG and movie data process.")
    all_m3u = M3uTransformer(iptv_filename).transform()
    show_data_service = TmdbShowDataService()

    series_service = ServiceSeries(M3uSeriesWriter("series.m3u"), show_data_service)
    movies_service = ServiceMovies(M3uMoviesWriter('movies.m3u'), show_data_service)
    channels_service = ServiceChannels(M3uChannelsWriter('channels.m3u'), show_data_service)

    with ThreadPoolExecutor(thread_name_prefix='save_thread') as executor:
        series_future = executor.submit(series_service.save, all_m3u)
        movies_future = executor.submit(movies_service.save, all_m3u)
        channel_future = executor.submit(channels_service.save, all_m3u)

        # executor.submit(self.update_m3u_entity, self.adultos, repository.adult_movies())

        logging.debug("Future result for movie thread - {}".format(movies_future.result()))
        logging.debug("Future result for channels thread - {}".format(channel_future.result()))
        logging.debug("Future result for series thread - {}".format(series_future.result()))

    logging.info("M3u process finished.")


if __name__ == '__main__':
    arguments = docopt(__doc__, version='M3U List Manager 1.0')
    console_handler.setLevel(logging.INFO)
    if arguments['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    elif arguments['--quiet']:
        logging.basicConfig(level=logging.ERROR)

    if arguments['--update-db']:
        runpy.run_path(arguments['--update-db'])
    else:
        main(arguments['--m3u-file'])

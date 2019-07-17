import logging
from datetime import datetime


def format_release_date(date):
    try:
        release_date = datetime.strftime(datetime.strptime(date, '%Y-%m-%d'), '%d-%m-%Y')
    except ValueError:
        logging.error("Release date not in proper format - {}".format(date))
        release_date = date
    except TypeError:
        logging.error("Error on type of date provided - {}".format(date))
        release_date = ''

    return release_date

import logging
from datetime import datetime


def format_release_date(date):
    try:
        release_date = datetime.strftime(datetime.strptime(date, '%Y-%m-%d'), '%d-%m-%Y')
    except ValueError:
        logging.error("Release date not in proper format - {}".format(date))
        release_date = date

    return release_date

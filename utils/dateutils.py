import logging
from datetime import datetime


def format_release_date(date):
    try:
        return datetime.strftime(datetime.strptime(date, '%Y-%m-%d'), '%d-%m-%Y')
    except ValueError:
        logging.error("Release date not in proper format - {}".format(date))
        return date
    except TypeError:
        logging.error("Error on type of date provided - {}".format(date))
        return ''

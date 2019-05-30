from tinydb import TinyDB


def movies():
    return TinyDB('M3U_MOVIES.json')


def channels():
    return TinyDB('M3U_CHANNEL.json')


def series():
    return TinyDB('M3U_SERIES.json')


def adult_movies():
    return TinyDB('M3U_MOVIES_ADULT.json')


def other():
    return TinyDB('M3U_OTHER.json')


def movie_data():
    return TinyDB('MOVIE_DATA.json')


def no_data_movies():
    return TinyDB('NO_DATA_MOVIES.json')

from tinydb import TinyDB


def movies():
    return TinyDB('M3U_MOVIES.json', encoding='utf8', ensure_ascii=False)


def channels():
    return TinyDB('M3U_CHANNEL.json', encoding='utf8', ensure_ascii=False)


def series():
    return TinyDB('M3U_SERIES.json', encoding='utf8', ensure_ascii=False)


def adult_movies():
    return TinyDB('M3U_MOVIES_ADULT.json', encoding='utf8', ensure_ascii=False)


def other():
    return TinyDB('M3U_OTHER.json', encoding='utf8', ensure_ascii=False)


def movie_data():
    return TinyDB('MOVIE_DATA.json', encoding='utf8', ensure_ascii=False)


def no_data_movies():
    return TinyDB('NO_DATA_MOVIES.json', encoding='utf8', ensure_ascii=False)


def series_data():
    return TinyDB('SERIES_DATA.json', encoding='utf8', ensure_ascii=False)


def no_data_series():
    return TinyDB('NO_DATA_SERIES.json', encoding='utf8', ensure_ascii=False)

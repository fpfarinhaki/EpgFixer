import logging

from tinydb import Query, operations

from domain.SeriesData import SeriesData
from repository import repository
from services.Fixer import Fixer


class SeriesFixer(Fixer):

    def __init__(self, show_data_service):
        super().__init__(show_data_service)

    def search_shows_with_no_data(self):
        no_data_series = repository.series().search(Query().data_id == 'NO_DATA_FOUND')
        return set(list(map(lambda serie: serie['title'], no_data_series)))

    def assign_data_manually(self, title, query):
        logging.info("Manually searching for series - {} - with query: {}".format(title, query))
        m3uSeries = repository.series().search(Query().title.matches("\s*" + title + "\s*"))
        doc_ids = list(map(lambda doc: doc.doc_id, m3uSeries))
        if m3uSeries:
            serie_id = self.show_data_service.search_serie_id(query)
            if serie_id:
                serie_data = self.show_data_service.serie_info(serie_id)
                seasons = []
                for season in range(1, int(serie_data['number_of_seasons']) + 1):
                    seasons.append(self.show_data_service.season_info(serie_data['id'], season))
                serie = SeriesData(serie_data, seasons)
                data_id = repository.series_data().upsert(vars(serie), Query().id == serie.id)
                repository.series().update(operations.set('data_id', data_id), doc_ids=doc_ids)
            else:
                logging.info("Series data not found in data service. Check later for updates.")
        else:
            logging.info("Show is not part of collection. Skipping")

    def map_to_series_id_dict(self, title):
        serie_id = self.show_data_service.search_serie_id(title.strip())
        doc_ids = list(map(lambda doc: doc.doc_id, repository.series().search(Query().title == title)))
        if serie_id:
            return {serie_id: doc_ids}
        else:
            repository.series().update(operations.set('data_id', 'NO_DATA_FOUND'), doc_ids=doc_ids)
            return {}

    def fill_series_data(self, series):
        titles = set(list(map(lambda serie: serie['title'], series)))

        logging.info("{} series found without data. Filling data".format(len(titles)))

        series_id_dict = dict()
        for title in titles:
            series_id_dict.update(self.map_to_series_id_dict(title))
        for serie_id in filter(lambda key: key != '', series_id_dict.keys()):
            serie_data = self.show_data_service.serie_info(serie_id)
            seasons = []
            for season in range(1, int(serie_data['number_of_seasons']) + 1):
                seasons.append(self.show_data_service.season_info(serie_data['id'], season))
            serie = SeriesData(serie_data, seasons)
            data_id = repository.series_data().upsert(vars(serie), Query().id == serie.id)
            repository.series().update(operations.set('data_id', data_id), doc_ids=series_id_dict.get(serie_id))

import logging

from tinydb import Query, operations

from domain.MissingDataItem import MissingDataItem
from domain.SeriesData import SeriesData
from repository import repository
from services.Fixer import Fixer


class SeriesFixer(Fixer):

    def remove_show_by_name(self, name):
        removed_ids = repository.series().update(operations.set('data_id', 'REMOVED'), Query().title == name)
        logging.info("Removed {} series records with name = {}".format(len(removed_ids), name))

    def __init__(self, show_data_service):
        super().__init__(show_data_service)

    def search_shows_with_no_data(self):
        no_data_series = repository.series().search(Query().data_id == 'NO_DATA_FOUND')
        return set(list(map(lambda serie: MissingDataItem(serie['title'], serie['tvg_logo']), no_data_series)))

    def assign_data_manually(self, title, query):
        logging.info("Manually searching for series - {} - with query: {}".format(title, query))
        m3uSeries = repository.series().search(Query().title.matches("\s*" + title + "\s*"))
        doc_ids = list(map(lambda doc: doc.doc_id, m3uSeries))
        if m3uSeries:
            serie_id = self.show_data_service.search_serie_id(query)
            if serie_id:
                self.update_series_data(serie_id, doc_ids)
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
            self.update_series_data(serie_id, series_id_dict.get(serie_id))

    def update_series_data(self, serie_id, doc_ids):
        serie_data = self.show_data_service.serie_info(serie_id)
        seasons = []
        for season in range(1, int(serie_data['number_of_seasons']) + 1):
            seasons.append(self.show_data_service.season_info(serie_data['id'], season))
        serie = SeriesData(serie_data, seasons)
        data_id = repository.series_data().upsert(vars(serie), Query().id == serie.id)
        repository.series().update(operations.set('data_id', data_id[0]), doc_ids=doc_ids)

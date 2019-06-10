import logging

from tinydb import Query, operations

from domain.SeriesData import SeriesData
from repository import repository
from services.Fixer import Fixer


class SeriesFixer(Fixer):

    def __init__(self, show_data_service):
        super().__init__(show_data_service)

    def search_shows_with_no_data(self):
        return list(map(lambda no_data: 'tvg_name: {}'.format(no_data['tvg_name']),
                        filter(lambda m: m['data_id'] == 'NO_DATA_FOUND', repository.series().all())))

    def assign_data_manually(self, tvg_name, query):
        raise NotImplementedError
        # logging.info("Manually searching for series - {} - with query: {}".format(tvg_name, query))
        # m3uSerie = repository.series().get(Query().tvg_name == tvg_name)
        # if m3uSerie:
        #     serie_id = TmdbShowDataService.search_serie_id(query)
        #     if serie_id:
        #         series_info = TmdbShowDataService.serie_info(serie_id)
        #         seasons = []
        #         for season in range(1, int(series_info['number_of_seasons']) + 1):
        #             seasons.append(TmdbShowDataService.season_info(series_info['id'], season))
        #         serie = SeriesData(series_info, seasons)
        #
        #         if not (repository.series_data().contains(Query().id == serie.id)):
        #             series_data_id = repository.series_data().insert(vars(serie))
        #             repository.series().update(set('movie_data_id', series_data_id), Query().tvg_name == tvg_name)
        #         else:
        #             logging.info("Duplicate movie data. Consider improving query for manual fixing.")
        #             logging.debug("Movie data already in database - {} Check for duplicates and consider improving "
        #                           "query for manual fixing."
        #                           .format("id: " + movie_data['id'] + " title: " + movie_data['title']))
        #     else:
        #         logging.info("Movie data not found in data service. Check later for updates.")
        # else:
        #     logging.info("TVG_NAME provided not part of collection. Skipping")

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
            data_id = repository.series_data().insert(vars(serie))
            repository.series().update(operations.set('data_id', data_id), doc_ids=series_id_dict.get(serie_id))

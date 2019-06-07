from repository import repository


class SeriesFixer:

    def search_shows_with_no_data(self):
        return list(map(lambda no_data: 'tvg_name: {}'.format(no_data['tvg_name']),
                        filter(lambda m: m['data_id'] == 'NO_DATA_FOUND', repository.series().all())))

from services import ShowDataService


class Fixer:

    def __init__(self, show_data_service: ShowDataService):
        self.show_data_service = show_data_service

    def search_shows_with_no_data(self):
        pass

    def assign_data_manually(self, name, query):
        pass

    def fill_show_data(self, m3u_list):
        pass
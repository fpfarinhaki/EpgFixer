class SeriesData:
    def __init__(self, data, seasons):
        self.id = data['id']
        self.name = data['name']
        self.generos = list(map(lambda genre: genre['name'], data['genres']))
        self.original_title = data['original_name']
        self.overview = data['overview']
        self.poster_path = data['poster_path']
        self.vote_average = data['vote_average']
        self.seasons = list(filter(None.__ne__, seasons))

class MissingDataItem:
    def __init__(self, name, poster_path):
        self.name = name
        self.poster_path = poster_path

    def __eq__(self, o: object) -> bool:
        if isinstance(o, MissingDataItem):
            return self.name == o.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)

from src.config.settings import MONGO_URI


class CatalogDocumentStore:
    def __init__(self, uri=MONGO_URI):
        self.uri = uri

    def describe(self):
        return {"engine": "mongodb", "uri": self.uri}

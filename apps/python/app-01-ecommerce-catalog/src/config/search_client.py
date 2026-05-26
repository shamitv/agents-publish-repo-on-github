from src.config.settings import ELASTICSEARCH_URL


class SearchClient:
    def __init__(self, url=ELASTICSEARCH_URL):
        self.url = url

    def build_query_string_payload(self, query):
        return {
            "index": "products",
            "query": {
                "query_string": {
                    "query": query,
                    "fields": ["name", "description", "category"],
                }
            },
        }

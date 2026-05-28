from src.config.search_client import SearchClient


class SearchService:
    def __init__(self, product_repository, search_client=None):
        self.products = product_repository
        self.search_client = search_client or SearchClient()

    def search(self, query_text):
        # VULNERABILITY A03: User input is placed directly in query syntax used by SQL fallback and Elasticsearch query_string.
        payload = self.search_client.build_query_string_payload(query_text)
        rows, sql_debug = self.products.unsafe_search(query_text)
        return rows, sql_debug, payload

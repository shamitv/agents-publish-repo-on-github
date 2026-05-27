from src.repositories.product_repository import ProductRepository
from src.services.search_service import SearchService


class ProductService:
    def __init__(self, products=None, search=None):
        self.products = products or ProductRepository()
        self.search = search or SearchService(self.products)

    def list_products(self, query_text):
        if query_text:
            rows, debug_query, search_payload = self.search.search(query_text)
        else:
            rows, debug_query = self.products.list_all()
            search_payload = None
        return {
            "products": [self._serialize(row) for row in rows],
            "debug_query": debug_query,
            "search_payload": search_payload,
        }

    def create_product(self, data):
        return self.products.create(data)

    def _serialize(self, row):
        return {
            "id": row["id"],
            "sku": row["sku"],
            "name": row["name"],
            "description": row["description"],
            "category": row["category"],
            "price": row["price"],
            "quantity": row["quantity"],
        }

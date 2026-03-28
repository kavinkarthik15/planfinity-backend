import os

try:
	from pymongo import MongoClient
except ImportError:  # pragma: no cover
	MongoClient = None


class InMemoryCollection:
	def __init__(self):
		self._items = []

	def insert_one(self, document):
		self._items.append(dict(document))

	def find(self, query, projection=None):
		results = [
			item
			for item in self._items
			if all(item.get(key) == value for key, value in query.items())
		]
		if projection and projection.get("_id") == 0:
			return [{k: v for k, v in row.items() if k != "_id"} for row in results]
		return results


class InMemoryDB:
	def __init__(self):
		self.transactions = InMemoryCollection()


def _create_db():
	mongo_uri = os.getenv("MONGO_URI")
	db_name = os.getenv("MONGO_DB_NAME", "finance_ai")

	if MongoClient and mongo_uri:
		client = MongoClient(mongo_uri)
		return client[db_name]

	return InMemoryDB()


db = _create_db()

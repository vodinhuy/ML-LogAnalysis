from pymongo import MongoClient

CONNECTION_STRING = "mongodb://localhost:27017/"


def get_database():
	client = MongoClient(CONNECTION_STRING)
	return client['myapp']


def insertDoc(collection, doc):
	#doc = { "name": "John", "address": "Highway 37" }
	res = collection.insert_one(doc)
	return res.inserted_id


def insertDocs(collection, docList):
	# docList = [
	#     {"name": "Amy", "address": "Apple st 652"},
	#     {"name": "Hannah", "address": "Mountain 21"},
	#     {"name": "Michael", "address": "Valley 345"}
	# ]
	res = collection.insert_many(docList)
	return res.inserted_ids


def deleteAll(collection):
	x = collection.delete_many({})
	print(x.deleted_count, "documents deleted.")
	return x


def findAll(collection):
	docs = collection.find()
	return docs


def filterDocs(collection, query):
	# query = {"address": "Park Lane 38"}
	docs = collection.find(query)
	return docs


if __name__ == "__main__":
	dbname = get_database()
	logCollection = dbname["weblogs"]
	findAll(logCollection)

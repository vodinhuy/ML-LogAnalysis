from pymongo import MongoClient

CONNECTION_STRING = "mongodb://localhost:27017/"


class DBAdapter:
    def __init__(self) -> None:
        self.db = None

    def get_database(self):
        if not self.db:
            client = MongoClient(CONNECTION_STRING)
            self.db = client["myapp"]
        return self.db

    def insert_doc(self, col_name: str, doc: dict):
        res = self.db[col_name].insert_one(doc)
        return res.inserted_id

    def insert_docs(self, col_name: str, docs: list):
        res = self.db[col_name].insert_many(docs)
        return res.inserted_ids

    def delete_all(self, col_name: str):
        x = self.db[col_name].delete_many({})
        print(x.deleted_count, "documents deleted.")

    def find_all(self, col_name: str):
        docs = self.db[col_name].find()
        return docs

    def filter_docs(self, col_name: str, query):
        docs = self.db[col_name].find(query)
        return docs

    def _create_counter(self, name: str):
        try:
            res = self.db["counters"].insert_one({
                "_id": name,
                "seq": 0
            })
            return res.inserted_id == name
        except Exception:
            return False

    def _reset_counter(self, name: str):
        self.db["counters"].update_one(filter={"_id": name},
                                       update={"$set": {"seq": 0}})

    def _get_next_sequence(self, name: str):
        res = self.db["counters"].find_one_and_update(filter={"_id": name},
                                                      update={"$inc": {"seq": 1}})
        return res["seq"]

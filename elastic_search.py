from elasticsearch import Elasticsearch, exceptions
import settings
from migrations import migrations

es = Elasticsearch(
    hosts=settings.ES_SERVER, basic_auth=(settings.ES_USER, settings.ES_PASSWORD),
    timeout=60
)


class ElaseticQuery:

    def create_data(self, index, body):
        count = self.get_value(index=index)
        print("count--------------", count)
        count = int(count)
        if count != 0:
            pk_id = count + 1
        else:
            pk_id = 1
        print("pk_id", pk_id)
        objs = es.index(index=index, id=pk_id, body=body)
        return objs

    def delete_specific_data(self, index, body):
        objs = es.delete_by_query(index=index, body=body)
        return objs

    def search_query(self, index, body=None):
        if body == None:
            body = {"query": {"match_all": {}}}
        objs = es.search(index=index, body=body)
        return objs

    def get_id(self, index, body):
        objs = self.search_query(index=index, body=body)
        if objs.get("hits").get("hits"):
            obj_id = objs.get("hits").get("hits")[0].get("_id")
        return obj_id

    def get_all_data(self, index, body):
        result = []
        objs = self.search_query(index=index, body=body)
        objs = objs.get("hits").get("hits")
        if objs:
            result = objs
        return result

    def get_value(self, index, body=None):
        value = 0
        if body == None:
            body = {"sort": [{"_id": {"order": "desc"}}], "query": {"match_all": {}}}
        try:
            objs = self.search_query(index=index, body=body)
            values = objs.get("hits").get("hits")
            if values:
                value = values[0].get("_id")
        except:
            print("Table not created")
        return value

    def check_specific_data(self, index, body, data, value):
        objs = self.search_query(index=index, body=body)
        for obj in objs.get("hits", {}).get("hits", []):
            if obj.get("_source").get(data) == value:
                return True
        return False

    def get_specific_data(self, index, body, data):
        result = None
        objs = self.search_query(index=index, body=body)
        for obj in objs.get("hits", {}).get("hits", []):
            result = obj.get("_source").get(data)
        return result

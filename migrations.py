import inspect
from fastapi import FastAPI, HTTPException, Request
from elasticsearch import Elasticsearch, exceptions
import models
from pydantic import BaseModel
import settings

app = FastAPI()

es = Elasticsearch(
    hosts=settings.ES_SERVER, basic_auth=(settings.ES_USER, settings.ES_PASSWORD)
)


def get_all_model_names():
    all_classes = inspect.getmembers(models, inspect.isclass)
    model_classes = [
        cls.__name__ for name, cls in all_classes if issubclass(cls, BaseModel)
    ]
    model_classes.remove("BaseModel")
    return model_classes


def migrations():
    query = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    },
    "mappings": {
        "properties": {
            "field1": {"type": "text"},
            "field2": {"type": "keyword"}
        }
    }
}
    model_lst = get_all_model_names()
    for model in model_lst:
        try:
            user_objs = es.search(index=model.lower(), body=query)
        except:
            user_objs = es.index(index=model.lower(), body=query)

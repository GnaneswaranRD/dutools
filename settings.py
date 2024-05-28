import os

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "5nzZZ0ShsORO9NxOuaYNLuvPS2mouB3zSb93ba5SxCdfYELzKMWe3yBqZSxksvUWYTMhkpiTXffAYPTWmhyTBATpC",
)
ES_SERVER = os.environ.get("ES_SERVER", "http://dutools_db:9200")
ES_USER = os.environ.get("ES_USER", "elastic")
ES_PASSWORD = os.environ.get("ES_PASSWORD", "elasticsearch")

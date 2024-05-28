from functools import wraps
from elastic_search import ElaseticQuery

elasticquery = ElaseticQuery()


def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_objs = 0
        try:
            user_id = request.session["user_id"]
            print("user_id", user_id)
            query = {
                "query": {
                    "match": {
                        "_id": user_id,
                    }
                }
            }
            user_objs = elasticquery.get_id(index="user", body=query)
        except:
            print("Users not found")
        print("user_objs", user_objs)
        if user_objs != 0:
            return view_func(request, *args, **kwargs)
        else:
            return {"message": "Login required"}

    return _wrapped_view

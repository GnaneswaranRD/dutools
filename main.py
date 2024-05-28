# Thrid part modules
from fastapi import FastAPI, HTTPException, Request
from elasticsearch import exceptions
from starlette.middleware.sessions import SessionMiddleware
import re
from datetime import timedelta, datetime
import logging

# own modules
from models import User
from utils import user_password_validation, jwt_encode, random_hashkey
from migrations import migrations
import settings
from elastic_search import ElaseticQuery, es
from decorators import login_required
from fastapi.staticfiles import StaticFiles

# other models urls
from templates import template_router
from articles import articles_router

app = FastAPI()
app.mount("/static", StaticFiles(directory="/app/static", html=True), name="static")
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.include_router(template_router)
app.include_router(articles_router)
elasticquery = ElaseticQuery()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/api/migrations")
def start_migration():
    migrations()
    return "Migrations completed"


@app.get("/check_elasticsearch")
async def check_elasticsearch():
    try:
        # Check if Elasticsearch is up by pinging the cluster
        if not es.ping():
            logger.error("Could not connect to Elasticsearch")
            raise HTTPException(
                status_code=503, detail="Elasticsearch service unavailable"
            )

        # Get cluster health
        health = es.cluster.health()
        logger.info("Elasticsearch cluster health: %s", health)
        return {"status": "success", "health": health}
    except exceptions.ConnectionError as e:
        # Handle connection error
        logger.error("ConnectionError: Could not connect to Elasticsearch")
        raise HTTPException(
            status_code=503, detail="Elasticsearch service unavailable"
        ) from e
    except exceptions.TransportError as e:
        # Handle transport error
        logger.error("TransportError: %s", str(e.info))
        raise HTTPException(status_code=e.status_code, detail=e.info)
    except Exception as e:
        # Handle other possible exceptions
        logger.error("Error: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/register")
def register(user_data: User):
    user_dict = user_data.dict()
    username = user_dict.get("username", None)
    password = user_dict.get("password", None)
    email = user_dict.get("email", None)
    report = False
    res = None
    print("yessssss")

    # Email validation
    if not bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)):
        raise HTTPException(status_code=400, detail="Invalid email address")

    # Password Validation
    if password:
        password_validation = user_password_validation(password)
        if password_validation != True:
            raise HTTPException(status_code=400, detail=password_validation)
    else:
        raise HTTPException(status_code=400, detail="Invaild password")

    # Get total users count for PK
    try:
        count = elasticquery.get_value(index="user")
        if count:
            count = int(count)
            user_id = count + 1
    except:
        user_id = 1

    # Check user email already exists
    try:
        email_username_query = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"email": user_dict.get("email")}},
                        {"match": {"username": user_dict.get("username")}},
                    ],
                    "minimum_should_match": 1,
                }
            }
        }
        email_username_res = es.search(index="user", body=email_username_query)
        print("email_username_res", email_username_res)

        for data in email_username_res.get("hits", {}).get("hits", []):
            if data.get("_source").get("email") == user_dict.get("email") or data.get(
                "_source"
            ).get("username") == user_dict.get("username"):
                report = True
                break
    except:
        print("noooooooo")

    if report == True:
        raise HTTPException(status_code=400, detail="Username or Email already exists")

    # Save new user data in database
    try:
        if username and password and email:
            data = {"password": password}
            password = jwt_encode(data=data, secret_key=settings.SECRET_KEY)
            user_dict["password"] = password
            res = es.index(index="user", id=user_id, body=user_dict)
    except Exception as e:
        print("error", e)

    if res:
        if res["result"] != "created":
            raise HTTPException(status_code=400, detail="User registration failed")
    else:
        raise HTTPException(status_code=400, detail="User registration failed")

    return {
        "message": "user created successful",
        "status_code": 200,
        "username": username,
    }


@app.post("/api/login")
def login(request: Request, username: str, password: str, remember_me: bool = False):
    result = {}

    save_password = password
    now = datetime.now()
    exp_time = now + timedelta(hours=12)

    if remember_me:
        request.session["exp_time"] = str(exp_time)

    if password:
        password_validation = user_password_validation(password)
        if password_validation != True:
            raise HTTPException(status_code=400, detail=password_validation)
        else:
            print("password", password)
            data = {"password": password}
            password = jwt_encode(data=data, secret_key=settings.SECRET_KEY)

    else:
        raise HTTPException(status_code=400, detail="Invaild password")

    try:
        login_query = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"username": username}},
                        {"match_phrase": {"password": password}},
                    ]
                }
            }
        }
        value = elasticquery.get_value(index="user", body=login_query)
        if value != 0:
            result = {"message": "Login successfully", "status_code": 200}
    except:
        print("Username and password incorrect")

    if result.get("status_code") == 200:
        token_obj = {}
        token = random_hashkey()
        user_id = elasticquery.get_id(index="user", body=login_query)
        request.session["user_id"] = user_id
        token_query = {"query": {"match": {"user_id": user_id}}}
        try:
            token = elasticquery.get_specific_data(
                index="token", body=token_query, data="token"
            )
            if token == None:
                new_token_query = {"query": {"match": {"token": token}}}
                token_exits = elasticquery.check_specific_data(
                    index="token", body=new_token_query, data="token", value=token
                )
        except:
            print("Token table not created")
            token_exits = False
            if token_exits == False:
                token_obj["user_id"] = user_id
                token_obj["token"] = token
                token_obj["created_at"] = str(datetime.now())
                elasticquery.create_data(index="token", body=token_obj)
        result["token"] = token
        result["username"] = username
        result["password"] = save_password
        return result
    else:
        raise HTTPException(status_code=400, detail="Incorrect username and password")


@app.get("/api/logout")
def logout(request: Request):
    user_id = request.session.get("user_id")
    print("user_id", user_id)
    query = {"query": {"match": {"user_id": user_id}}}
    elasticquery.delete_specific_data(index="token", body=query)
    request.session.clear()
    return {"status_code": 200, "message": "Logout successfully"}

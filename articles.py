from fastapi import APIRouter, HTTPException, Request, UploadFile
from typing import List
import logging
import os
import shutil

# own modules
from models import Articles
import settings
from elastic_search import ElaseticQuery, es
from decorators import login_required

elasticquery = ElaseticQuery()

articles_router = APIRouter()


UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@articles_router.post("/api/upload_article")
@login_required
def upload_article(
    request: Request,
    title: str,
    author: str,
    content: str,
    image: UploadFile
):

    image_path = os.path.join(UPLOAD_DIR, image.filename)

    user_id = int(request.session["user_id"])

    article = Articles(
        user_id=user_id,
        title=title,
        author=author,
        content=content,
        image=image_path,
    )
    # data = elasticquery.search_query(index="articles")
    # print("data", data)
    data = elasticquery.create_data(index="articles", body=article.dict())
    return {"message": "Data uploaded successfully", "status_code": 200}


@articles_router.get("/api/view_article")
@login_required
def view_article(request: Request, view_all: bool = False):
    result = []
    if view_all:
        query = {"query": {"match_all": {}}}
        article_obj = elasticquery.get_all_data(index="articles", body=query)
        if article_obj:
            for obj in list(article_obj):
                result.append(
                    {
                        "id": obj.get("_id"),
                        "user_id": obj.get("_source").get("user_id"),
                        "title": obj.get("_source").get("title"),
                        "author": obj.get("_source").get("author"),
                        "content": obj.get("_source").get("content"),
                    }
                )
        return list(result)
    user_id = int(request.session["user_id"])
    query = {"query": {"match": {"user_id": user_id}}}
    article_obj = elasticquery.get_all_data(index="articles", body=query)
    if article_obj:
        for obj in list(article_obj):
            result.append(
                {
                    "id": obj.get("_id"),
                    "user_id": obj.get("_source").get("user_id"),
                    "title": obj.get("_source").get("title"),
                    "author": obj.get("_source").get("author"),
                    "content": obj.get("_source").get("content"),
                }
            )

    return list(result)


@articles_router.put("/api/edit_article/{id}")
@login_required
def edit_article(
    request: Request,
    id: int,
    title: str,
    author: str,
    content: str,
    image: UploadFile,
):
    result = []

    image_path = os.path.join(UPLOAD_DIR, image)

    user_id = int(request.session["user_id"])
    query = {"query": {"match": {"_id": id}}}
    article_obj = elasticquery.get_all_data(index="articles", body=query)
    if article_obj:
        for obj in list(article_obj):
            result.append(
                {
                    "id": obj.get("_id"),
                    "user_id": obj.get("_source").get("user_id"),
                    "title": obj.get("_source").get("title"),
                    "author": obj.get("_source").get("author"),
                    "content": obj.get("_source").get("content"),
                }
            )

    print("result", result)

    # article = Articles(
    #     user_id=user_id,
    #     title=title,
    #     author=author,
    #     content=content,
    #     image=image_path,
    # )
    # # data = elasticquery.search_query(index="articles")
    # # print("data", data)
    # data = elasticquery.create_data(index="articles", body=article.dict())
    # return {"message": "Data uploaded successfully","status_code":200}

    return result


@articles_router.get("/api/test")
@login_required
def test(request: Request):
    return "Tested"


@articles_router.get("/api/dashboard")
@login_required
def dashboard(request: Request):
    return "Dashboard"

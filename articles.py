from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from typing import List, Optional
import logging
import os
import shutil
from fastapi.responses import JSONResponse, RedirectResponse

# own modules
from models import Articles
import settings
from elastic_search import ElaseticQuery, es
from decorators import login_required
import time

elasticquery = ElaseticQuery()

articles_router = APIRouter()



@articles_router.post("/api/upload_article")
@login_required
def upload_article(request: Request, title: str, author: str, content: str):


    user_id = int(request.session["user_id"])

    article = Articles(
        user_id=user_id,
        title=title,
        author=author,
        content=content,
    )
    # data = elasticquery.search_query(index="articles")
    # print("data", data)
    data = elasticquery.create_data(index="articles", body=article.dict())
    time.sleep(1)
    return {"message": "Data uploaded successfully", "status_code": 200}


@articles_router.get("/api/view_article")
@login_required
def view_article(request: Request, view_all: bool = False):
    result = []
    if view_all:
        try:
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
        except Exception as e:
            print("error", e)
            raise HTTPException(status_code=400, detail="No article found")
        return list(result)
    user_id = int(request.session["user_id"])
    try:
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
    except Exception as e:
        print("error", e)
        raise HTTPException(status_code=400, detail="No article found")
    return list(result)


@articles_router.get("/api/detail_article/{id}")
@login_required
def detail_article(request: Request, id: int):
    query = {"query": {"match": {"_id": id}}}
    article_obj = elasticquery.get_all_data(index="articles", body=query)

    if not article_obj:
        raise HTTPException(status_code=404, detail="Article not found")

    result = []
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

    return result


@articles_router.put("/api/edit_article/{id}")
@login_required
def edit_article(
    request: Request, id: int, title: str, author: str, content: str
):
    user_id = int(request.session.get("user_id"))

    if not (title and author and content):
        raise HTTPException(status_code=400, detail="Missing required fields")


    article = Articles(
        user_id=user_id,
        title=title,
        author=author,
        content=content,
    )

    data = elasticquery.edit_data(index="articles", id=id, body=article.dict())
    return {"message": "Data updated successfully", "status_code": 200, "data": data}


@articles_router.get("/api/delete_article/{id}")
@login_required
def delete_article(request: Request, id: int):
    body = {"query": {"match": {"_id": id}}}
    data = elasticquery.delete_specific_data(index="articles", body=body)
    time.sleep(1)
    return RedirectResponse(url="/view_articles")

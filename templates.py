from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from decorators import login_required
from utils import get_current_user

template_router = APIRouter()

templates = Jinja2Templates(directory="/app/templates")


@template_router.get("/login", response_class=HTMLResponse)
async def login_view(request: Request):
    return templates.TemplateResponse("accounts/login.html", {"request": request})


@template_router.get("/register", response_class=HTMLResponse)
async def login_view(request: Request):
    return templates.TemplateResponse("accounts/register.html", {"request": request})

@template_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_view(request: Request, user: dict = Depends(get_current_user)):
    if user.get("user") != "none":
        return templates.TemplateResponse("dashboard/dashboard.html", {"request": request,"user":user})
    else:
        return RedirectResponse(url="/")


@template_router.get("/", response_class=HTMLResponse)
async def landing_page_view(request: Request):
    return templates.TemplateResponse(
        "dashboard/landing_page.html", {"request": request}
    )


@template_router.get("/view_articles", response_class=HTMLResponse)
async def view_articles(request: Request,user: dict = Depends(get_current_user)):
    if user.get("user") != "none":
        return templates.TemplateResponse(
            "articles/view_articles.html", {"request": request,"user":user}
        )
    else:
        return RedirectResponse(url="/")
    

@template_router.get("/create_article", response_class=HTMLResponse)
async def create_article(request: Request,user: dict = Depends(get_current_user)):
    if user.get("user") != "none":
        return templates.TemplateResponse(
            "articles/create_article.html", {"request": request,"user":user}
        )
    else:
        return RedirectResponse(url="/")
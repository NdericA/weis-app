from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {})


@router.get("/login", response_class=HTMLResponse)
def login(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {})


@router.get("/signup", response_class=HTMLResponse)
def signup(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "signup.html", {})


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "dashboard.html", {})


@router.get("/dashboard/rider", response_class=HTMLResponse)
def rider_dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "rider_dashboard.html", {})


@router.get("/dashboard/driver", response_class=HTMLResponse)
def driver_dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "driver_dashboard.html", {})

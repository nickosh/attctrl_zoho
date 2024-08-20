from typing import Optional

import sentry_sdk
from fastapi import Depends, FastAPI, Form, HTTPException, Request, Security, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from attctrl.browser import zoho_check_in, zoho_check_out, zoho_test
from attctrl.config import Config
from attctrl.logger import new_logger, notification_queue
from attctrl.scheduler import TaskScheduler


logger = new_logger(__name__)

if Config.GLITCHTIP_DNS:
    sentry_sdk.init(Config.GLITCHTIP_DNS)

API_KEY_NAME = "X-API-Key"

tasker = TaskScheduler()
app = FastAPI(workers=1)
app.mount("/static", StaticFiles(directory=Config.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=Config.TEMPLATE_DIR)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_token(api_key_header: str = Security(api_key_header)):
    if not Config.APP_AUTH:
        return True
    if api_key_header == Config.AUTH_TOKEN:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if not Config.APP_AUTH:
        return await call_next(request)

    public_paths = ["/login", "/static"]

    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)

    auth_token = request.cookies.get(API_KEY_NAME)

    if auth_token == Config.AUTH_TOKEN:
        return await call_next(request)
    elif request.url.path != "/login":
        return RedirectResponse(url="/login", status_code=302)

    return await call_next(request)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "Config": Config})


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/notifications")
async def get_notifications(token: bool = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
    notifications = list(notification_queue)
    notification_queue.clear()
    return JSONResponse(content={"notifications": notifications})


@app.get("/tasks", response_class=HTMLResponse)
async def view_tasks(request: Request, token: bool = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")

    return templates.TemplateResponse(
        request=request,
        name="components/task_view.html",
        context={"tasks": tasker.get_tasks()},
    )


@app.post("/tasks", response_class=HTMLResponse)
async def create_task(
    request: Request,
    token: bool = Depends(verify_token),
    time: str = Form(...),
    task_type: str = Form(..., alias="task_type"),
    jitter: Optional[int] = Form(None),
    timezone: Optional[str] = Form(None),
    monday: str = Form(None),
    tuesday: str = Form(None),
    wednesday: str = Form(None),
    thursday: str = Form(None),
    friday: str = Form(None),
    saturday: str = Form(None),
    sunday: str = Form(None),
):
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")

    days = ",".join(
        [day for day in [monday, tuesday, wednesday, thursday, friday, saturday, sunday] if day]
    )
    task_function = {
        "checkin": zoho_check_in,
        "checkout": zoho_check_out,
        "test": zoho_test,
    }.get(task_type)

    if task_function:
        tasker.add_task(
            task_func=task_function,
            day_of_week=days,
            time=time,
            jitter=jitter,
            timezone=timezone,
        )

    return templates.TemplateResponse(
        request=request,
        name="components/task_view.html",
        context={"tasks": tasker.get_tasks()},
    )


@app.get("/tasks/add_test_task")
async def add_test_task(_: Request, token: bool = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
    tasker.add_task(zoho_test, "mon,tue,wed,thu,fri", "19:25:00")
    return {"message": "Test task added successfully"}


@app.delete("/tasks/{task_id}", response_class=HTMLResponse)
async def delete_task(request: Request, task_id: str, token: bool = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")

    tasker.remove_task(task_id)
    return templates.TemplateResponse(
        request=request,
        name="components/task_view.html",
        context={"tasks": tasker.get_tasks()},
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "Config": Config})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == Config.ZOHO_USERNAME and password == Config.ZOHO_PASSWORD:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(
            key=API_KEY_NAME,
            value=Config.AUTH_TOKEN,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        return response
    else:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "Config": Config, "error": "Invalid credentials"},
            status_code=400,
        )


@app.post("/logout")
async def logout(_: Request):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(API_KEY_NAME)
    response.headers["HX-Redirect"] = "/login"
    return response

from typing import List, Optional

from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fasthx import Jinja

from attctrl.browser import zoho_check_in, zoho_check_out, zoho_test
from attctrl.config import Config
from attctrl.logger import new_logger
from attctrl.scheduler import Task, TaskScheduler

logger = new_logger(__name__)

tasker = TaskScheduler()
app = FastAPI(workers=1)
jinja = Jinja(Jinja2Templates(Config.TEMPLATE_DIR))


@app.get("/tasks/add_test_task")
def add_test_task():
    tasker.add_task(zoho_test, "mon,tue,wed,thu,fri", "19:25:00")
    return {"message": "Test task added successfully"}


@app.post("/tasks")
@jinja.hx("components/task_view.html")
def create_task(
    request: Request,
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
) -> List[Task]:
    days = ",".join(
        [day for day in [monday, tuesday, wednesday, thursday, friday, saturday, sunday] if day]
    )
    task_function = {"checkin": zoho_check_in, "checkout": zoho_check_out, "test": zoho_test}.get(
        task_type
    )

    if task_function:
        tasker.add_task(
            task_func=task_function, day_of_week=days, time=time, jitter=jitter, timezone=timezone
        )

    return tasker.get_tasks()


@app.delete("/tasks/{task_id}")
@jinja.hx("components/task_view.html")
def delete_task(task_id: str) -> List[Task]:
    tasker.remove_task(task_id)
    return tasker.get_tasks()


@app.get("/tasks")
@jinja.hx("components/task_view.html")
def view_tasks() -> List[Task]:
    return tasker.get_tasks()


@app.get("/")
@jinja.page("index.html")
def index() -> None: ...

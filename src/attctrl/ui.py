from typing import List

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fasthx import Jinja

from attctrl.browser import zoho_check_in, zoho_check_out, zoho_test
from attctrl.config import Config
from attctrl.scheduler import Task, TaskScheduler

tasker = TaskScheduler()
app = FastAPI()
jinja = Jinja(Jinja2Templates(Config.TEMPLATE_DIR))


@app.post("/tasks")
def create_task() -> None: ...


@app.delete("/tasks/{task_id}")
@jinja.hx("components/tasks_view.html")
def delete_task(task_id: str):
    tasker.remove_task(task_id)
    return tasker.get_tasks()


@app.get("/tasks")
@jinja.hx("components/tasks_view.html")
def view_tasks() -> List[Task]:
    return tasker.get_tasks()


@app.get("/")
@jinja.page("index.html")
def index() -> None: ...

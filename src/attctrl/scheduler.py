from typing import List

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pydantic import BaseModel

from attctrl.config import Config
from attctrl.logger import new_logger

logger = new_logger(__name__)


class CronIndexMap:
    dow = CronTrigger.FIELD_NAMES.index("day_of_week")
    hour = CronTrigger.FIELD_NAMES.index("hour")
    minute = CronTrigger.FIELD_NAMES.index("minute")
    second = CronTrigger.FIELD_NAMES.index("second")


class Task(BaseModel):
    id: str
    func: str
    dow: str
    time: str


class TaskScheduler:
    def __init__(self, jobs_dir: str = Config.DATA_DIR.as_posix()):
        self.jobstore = SQLAlchemyJobStore(url=f"sqlite:///{jobs_dir}/jobs.sqlite")
        self.scheduler = BackgroundScheduler(jobstores={"default": self.jobstore})
        self.scheduler.start()

    def add_task(self, task_func, day_of_week: str, time: str):
        """
        Add a new task to the scheduler.

        :param task_func: The function to be executed
        :param day_of_week: Day(s) of the week to run the task (e.g., 'mon,tue,wed')
        :param time: Time to run the task in HH:MM:SS format
        """
        hour, minute, second = map(int, time.split(":"))
        try:
            self.scheduler.add_job(
                task_func,
                trigger=CronTrigger(
                    day_of_week=day_of_week, hour=hour, minute=minute, second=second
                ),
                replace_existing=True,
            )
            logger.info("Task added successfully")
        except Exception as e:
            logger.error(f"Failed to add task : {e}")

    def remove_task(self, task_id: str):
        """
        Remove a task from the scheduler.

        :param task_id: The unique identifier of the task to remove
        """
        try:
            self.scheduler.remove_job(task_id)
            logger.info(f"Task '{task_id}' removed successfully")
        except Exception as e:
            logger.error(f"Failed to remove task '{task_id}': {e}")

    def get_tasks(self) -> List[Task]:
        """
        Get a list of all scheduled tasks.

        :return: A list of dictionaries containing task information
        """
        jobs = self.scheduler.get_jobs()
        return [
            Task(
                id=job.id,
                func=job.func.__name__,
                dow=str(job.trigger.fields[CronIndexMap.dow]),
                time=f"{str(job.trigger.fields[CronIndexMap.hour]).zfill(2)}:{str(job.trigger.fields[CronIndexMap.minute]).zfill(2)}:{str(job.trigger.fields[CronIndexMap.second]).zfill(2)}",
            )
            for job in jobs
        ]

    def shutdown(self):
        """
        Shut down the scheduler.
        """
        self.scheduler.shutdown(wait=True)


# Example usage:
# def some_function():
#     print("Executing some_function")
#
# def another_function():
#     print("Executing another_function")
#
# scheduler = TaskScheduler()
# scheduler.add_task(some_function, 'task1', 'mon,wed,fri', '09:00')
# scheduler.add_task(another_function, 'task2', 'tue,thu', '14:30')
# print(scheduler.get_tasks())
# scheduler.remove_task('task1')
# scheduler.shutdown()

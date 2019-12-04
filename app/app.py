# encoding: UTF-8

from json import dumps
from sqlalchemy import and_
import cherrypy

from db.model import LessonTask, Solution, Task
from db.plugin import SAEnginePlugin
from db.tool import SATool


@cherrypy.expose
class App():
    @cherrypy.expose
    def tasks(self, type=None):
        stats = (
            cherrypy.request.db.query(Task.id, Task.type, Task.cost, LessonTask.lesson_id, \
                                    LessonTask.n_views, Solution.time)
                               .outerjoin(LessonTask, Task.id == LessonTask.task_id)
                               .outerjoin(Solution,
                                 and_(
                                     LessonTask.lesson_id == Solution.lesson_id,
                                     LessonTask.task_id == Solution.task_id
                                 )
                               )
                               .order_by(Task.id)
        )
        first_row = stats.first()

        responses = []
        current_task = {
            "task_id": first_row.id,
            "task_type": first_row.type,
            "task_cost": first_row.cost,
            "n_lessons": 0,
            "n_views": 0,
            "n_solutions": 0,
            "top_lesson": None,
            "bottom_lesson": None
        }
        lessons = {}

        for row in stats.all():
            if current_task["task_id"] != row.id:
                if lessons:
                    current_task["top_lesson"] = max(lessons, key=lessons.get)
                    current_task["bottom_lesson"] = min(lessons, key=lessons.get)
                responses.append(current_task)

                lessons = {}
                current_task = dict(zip(current_task.keys(), (
                    row.id, row.type, row.cost, 0, 0, 0, None, None
                )))
            if row.lesson_id:
                lessons[row.lesson_id] = lessons.get(row.lesson_id, 0) + (1 if row.time else 0) / row.n_views
                current_task["n_lessons"] += 1
                current_task["n_views"] += row.n_views
                current_task["n_solutions"] += (1 if row.time else 0)
        responses.append(current_task)

        cherrypy.response.headers["Content-Type"] = "text/plain; charset=utf-8"
        return dumps(responses)

    @cherrypy.expose
    def add_tasks(self, lesson_id, task_spec):
        if (len(task_spec) % 2 != 0):
            return "Wrong arguments!"

        tasks = []
        for task_id, cost in zip(*[iter(task_spec)] * 2):
            tasks.append(
                LessonTask(lesson_id, task_id, cost)
            )

        cherrypy.request.db.add_all(tasks)
        cherrypy.response.headers["Content-Type"] = "text/plain; charset=utf-8"
        return "Success!"

    @cherrypy.expose
    def task_solution(self, task_id, lesson_id, user_id, grade):
        if grade.startswith(" "):
            cherrypy.request.db.query(Solution).filter(
                and_(
                    Solution.task_id == task_id,
                    Solution.lesson_id == lesson_id,
                    Solution.student_id == user_id
                )
            ).update({"mark": Solution.mark + int(grade[1:])})
        else:
            cherrypy.request.db.add(
                Solution(user_id, task_id, lesson_id, grade)
            )

        cherrypy.response.headers["Content-Type"] = "text/plain; charset=utf-8"
        return "Success!"


if __name__ == "__main__":
    db_dialect = "postgresql"
    db_driver = "psycopg2"
    dsn = {
        "host": "localhost",
        "port": "5432",
        "username": "postgres",
        "password": "postgres",
        "database": "postgres"
    }

    connection_string = f"{db_dialect}+{db_driver}://" \
                        f"{dsn['username']}:{dsn['password']}@{dsn['host']}:{dsn['port']}/" \
                        f"{dsn['database']}"

    cherrypy.config.update({"tools.db.on": True})
    SAEnginePlugin(cherrypy.engine, connection_string).subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.quickstart(App())
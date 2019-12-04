from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, ForeignKeyConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
import datetime

from . import Base


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint('email'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=True)

    def __init__(self, email, name):
        self.email = email
        self.name = name


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        CheckConstraint("start_time <= end_time"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    lesson_tasks_collection = relationship("LessonTask", backref="lessons")

    def __init__(self, start_time, end_time, tasks):
        self.start_time = start_time
        self.end_time = end_time
        self.lesson_tasks_collection = tasks


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)
    cost = Column(Integer, nullable=False, default=10)
    solution = Column(String, nullable=True)

    def __init__(self, description, type, cost, solution):
        self.description = description
        self.type = type
        self.cost = cost
        self.solution = solution


class LessonTask(Base):
    __tablename__ = "lesson_task"

    lesson_id = Column(Integer, ForeignKey("lessons.id"), primary_key=True, autoincrement=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), primary_key=True, autoincrement=False)
    task_cost = Column(Integer, nullable=True)
    n_views = Column(Integer, nullable=False, default=1)

    def __init__(self, lesson_id, task_id, task_cost):
        self.lesson_id = lesson_id
        self.task_id = task_id
        self.task_cost = task_cost


class Solution(Base):
    __tablename__ = "solutions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["lesson_id", "task_id"],
            ["lesson_task.lesson_id", "lesson_task.task_id"]
        ),
    )

    time = Column(DateTime, default=datetime.datetime.utcnow)
    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    task_id = Column(Integer, nullable=False, primary_key=True, autoincrement=False)
    lesson_id = Column(Integer, nullable=False, primary_key=True, autoincrement=False)
    mark = Column(Integer, nullable=False, default=0)

    def __init__(self, student_id, task_id, lesson_id, mark):
        self.student_id = student_id
        self.task_id = task_id
        self.lesson_id = lesson_id
        self.mark = mark

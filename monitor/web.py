from .models import Task
from http import HTTPStatus

from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler
from tornado.gen import coroutine
from tornado.queues import Queue


class TaskHandler(RequestHandler):
    def __init__(self, queue: Queue['Task']):
        self.queue = queue
        self.tasks = {}

    def get(self):
        ...

    @coroutine
    def post(self):
        request: HTTPServerRequest = self.request
        task = Task.from_json(request.body)
        yield self.queue.put(task)
        self.tasks[task.run_id] = task
        self.write(task.to_json())
        self.add_header("Content-Type", "application/json")
        self.set_status(HTTPStatus.CREATED)

from .models import Task

from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler
from tornado.queues import Queue


class TaskHandler(RequestHandler):
    def __init__(self, queue: Queue):
        self.queue = queue

    def get(self):
        ...

    def post(self):
        request: HTTPServerRequest = self.request
        task = Task.from_json(request.body)

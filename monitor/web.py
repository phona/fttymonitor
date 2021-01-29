from .models import Task

from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler


class TaskHandler(RequestHandler):
    def get(self):
        ...

    def post(self):
        request: HTTPServerRequest = self.request
        task = Task.from_json(request.body)

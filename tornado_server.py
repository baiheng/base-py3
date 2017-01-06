#!/bin/env python
# -*-coding:utf-8-*-

import os
import importlib

import uvloop
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.platform
from tornado.options import define, options

from conf import settings

define("port", default=settings.PORT, help="run on th given port", type=int)
options.logging = "info"

url_list = []
for i in os.listdir("./src/"):
    if i.startswith("__"):
        continue
    module_path = f"./src/{i}/"
    if not os.path.isdir(module_path):
        continue
    view_path = f"{module_path}views/"
    for j in os.listdir(view_path):
        if j.startswith("__") or j.endswith("pyc"):
            continue
        f = j[:-3]
        view = importlib.import_module(f"src.{i}.views.{f}")
        view_class = None
        for c in dir(view):
            if c.endswith("View"):
                view_class = c
                break
        if view_class is None:
            continue
        handler = getattr(view, view_class)
        url_list.append((f"{settings.URL_PREFIX}/{i}/{f}", handler))


class TornadoUvloop(tornado.platform.asyncio.BaseAsyncIOLoop):
    def initialize(self, **kwargs):
        loop = uvloop.new_event_loop()
        try:
            super(TornadoUvloop, self).initialize(
                    loop, close_loop=True, **kwargs)
        except Exception:
            loop.close()
            raise


setting = dict(
    static_url_prefix = f"{settings.URL_PREFIX}/static/",
    template_path = os.path.join(os.path.dirname(__file__),"template"),
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    autoreload = True,
    )


if __name__ == '__main__':
    application = tornado.web.Application(handlers=url_list, **setting)
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.configure(TornadoUvloop)
    tornado.ioloop.IOLoop.instance().start()

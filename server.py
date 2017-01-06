#!/bin/env python
# -*-coding:utf-8-*-

import os
import importlib

from sanic import Sanic

from conf import settings


app = Sanic(__name__)

def dispatch(handler):
    def _dispatch(request, *args, **kwargs):
        obj = handler()
        return obj.dispatch()
    return _dispatch

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
        app.add_route(dispatch(handler), f"{settings.URL_PREFIX}/{i}/{f}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8289, debug=True)

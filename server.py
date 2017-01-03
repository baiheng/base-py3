#!/bin/env python
# -*-coding:utf-8-*-

import os
import importlib

from sanic import Sanic


app = Sanic(__name__)

def dispatch(handler):
    def _dispatch():
        obj = handler()
        return obj.dispatch()
    return _dispatch

for i in os.listdir("./src/"):
    view_path = "./src/%s/views/" % i
    for j in os.walk(view_path):


for i in modules:
    # 获取导入模块属性名称  导入异常赋给一个默认值 'attribute'
    for j in getattr(importlib.import_module('%s' % i), 'attribute'):
        # 给views属性，注册到蓝图
        bp = getattr(importlib.import_module('%s.views.%s_view' % (i, j)), j)
        app.register_blueprint(bp, url_prefix="/pluginserver/ops/%s" % i)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8189, debug=True)

#!/bin/env python
# -*-coding:utf-8-*-

import asyncio

import tornado.web
import tornado.gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest

class BhView(tornado.web.RequestHandler):
    async def dispatch(self):
        print(1)
        c = self.a()
        print(c)
        return text("ok")

    def a(self):
        return 1 + 3

    async def get(self):
        #await self.test()
        #await tornado.gen.sleep(2)
        self.write("ok")
        self.finish()

    async def test(self):
        request = HTTPRequest(url="http://0.0.0.0:8289/api/v1/t/c")
        http_client = AsyncHTTPClient()
        resp = await http_client.fetch(request)

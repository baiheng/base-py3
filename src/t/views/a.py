#!/bin/env python
# -*-coding:utf-8-*-

import asyncio

from sanic.response import text


class OmgView(object):
    async def dispatch(self):
        #await asyncio.sleep(2)
        return text("ok")

    def a(self):
        return 1 + 3

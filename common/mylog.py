#!/bin/env python
# -*-coding:utf-8-*- 

import logging
import logging.config
import os

logging.config.fileConfig("./conf/logging.ini")
logger = logging.getLogger("root")

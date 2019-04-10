#!/bin/env python
# -*- coding:utf8 -*-


class BaseConfig(object):
    DEBUG = False
    PORT = 8189

    URL_PREFIX = "/api/v1"

    # 生产新数据库
    MYSQL_HOST = "172.16.99.73"
    MYSQL_PORT = 3306
    MYSQL_USER = "**"
    MYSQL_PWD = "**"
    MYSQL_DB = "**"

    # 3小时后自动重连mysql
    MYSQL_CONNECT_TIMEOUT = 3 * 24 * 60 * 60

    # token
    # 7天有效期
    TOKEN_TIMEOUT = 7 * 24 * 60 * 60 
    PRIVATE_KEY = '8834567812345678'

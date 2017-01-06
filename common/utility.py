#!/bin/env python
# -*-coding:utf-8-*- 

import datetime
from decimal import Decimal

from sqlalchemy.ext.declarative import DeclarativeMeta

from .sqlalchemy_ctl import Base
from .sqlalchemy_ctl import DBSession
from .sqlalchemy_ctl import engine


def create_table(table_name=""):
    if table_name == "":
        Base.metadata.create_all(engine)
    else:
        Base.metadata.tables[table_name].create(bind=engine, checkfirst=True)


def drop_table(table_name=""):
    if table_name == "":
        Base.metadata.drop_all(engine)
    else:
        Base.metadata.tables[table_name].drop(bind=engine, checkfirst=True)

def to_obj(
        orm_obj,
        need_fields=None,
        without_fields=None, 
        datetime_format="%Y-%m-%d"):
    if isinstance(orm_obj, list):
        return [to_obj(i, need_fields, without_fields, datetime_format) for i in orm_obj]
    elif isinstance(orm_obj.__class__, DeclarativeMeta):
        attr_dict = dict()
        for attr in [x for x in dir(orm_obj) if not x.startswith('_') and x != 'metadata']:
            data = getattr(orm_obj, attr)
            if need_fields and attr not in need_fields:
                continue
            if without_fields and attr in without_fields:
                continue
            if isinstance(data, datetime.datetime):
                if datetime_format == "timestamp":
                    attr_dict[attr] = int(time.mktime(data.timetuple()))
                else:
                    attr_dict[attr] = data.strftime(datetime_format)
                    attr_dict["%s_timestramp" % attr] = int(time.mktime(data.timetuple()))
            elif isinstance(data, datetime.date):
                attr_dict[attr] = data.strftime("%Y-%m-%d")
            elif isinstance(data, datetime.timedelta):
                attr_dict[attr] = ((datetime.datetime.min + data).time().
                                   strftime("%Y-%m-%d %H:%M:%S"))
            elif isinstance(data, Decimal):
                attr_dict[attr] = float(data)
            else:
                attr_dict[attr] = data
            if attr.endswith("_json"):
                if data:
                    attr_dict[attr] = json.loads(data)
            if attr.endswith("_url"):
                if not data:
                    attr_dict["%s_path" % attr] = ""
                else:
                    attr_dict["%s_path" % attr] = "%s%s" % (settings.SERVER_HOST, data)
        return attr_dict
    else:
        return orm_obj

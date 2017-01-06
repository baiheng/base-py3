#!/bin/env python
# -*-coding:utf-8-*-

import importlib

from sqlalchemy import desc

from common.mylog import logger


class BaseController(object):
    def __init__(self, model=None):
        if model:
            self._model = model
        else:
            name = self.__class__.__name__
            name_prefix = name[:-len("Controller")]
            self._model = importlib.import_module(f"...models.{name_prefix}")

    def _clean_value(self, value):
        if isinstance(value, str):
            return value.strip()
        return value

    def _filter_value(self, kwargs):
        return filter(lambda x: (
                    x != "metadata" 
                    and x != "id"
                    and not x.startswith("_")
                    and kwargs.has_key(x)
                    ),
                dir(self._model))

    def filter_item(self, **kwargs):
        session = kwargs.get("session", None)
        if session is None:
            return None, None
        start = int(kwargs.get("start", -1))
        end = int(kwargs.get("end", -1))
        pk = kwargs.get("id", None)
        try:
            filter_obj = session.query(self._model)
            if pk is not None:
                data = filter_obj.filter_by(id=pk).first()
                if data:
                    return data, 1
                else:
                    return data, 0
            value = {k: self._clean_value(kwargs[k]) for k in self._filter_value(kwargs)}
            filter_obj = filter_obj.filter_by(**value)
            kv = kwargs.get("like", None)
            if kv is not None:
                k, v = kv.split("^")
                filter_obj = filter_obj.filter(getattr(self._model, k).like(f"%{v}%"))
            id_list = kwargs.get("id_list", None)
            if id_list is not None:
                filter_obj = filter_obj.filter(getattr(self._model, "id").in_(id_list))
            filter_condition = kwargs.get("filter_condition", None)
            if filter_condition is not None:
                filter_obj = filter_obj.filter(filter_condition)
            filter_obj = filter_obj.order_by(desc("id"))
            if start == -1 and end == -1:
                all_list = filter_obj.all()
                if isinstance(all_list, list):
                    return all_list, len(all_list)
                else:
                    return all_list, 1
            else:
                return filter_obj[start:end], filter_obj.count()
        except Exception as e:
            logger.error("查询%s出错. %s, %s" % (self._model.__tablename__, e, kwargs))
            return None, None

    def new_item(self, **kwargs):
        session = kwargs.get("session", None)
        if session is None:
            return False
        try:
            value = {k: self._clean_value(kwargs[k])
                    for k in self._filter_value(kwargs)}
            new_obj = self._model(**value)
            session.add(new_obj)
            return new_obj
        except Exception as e:
            logger.error("新建%s出错. %s, %s" % (self._model.__tablename__, e, kwargs))
            return False

    def update_item(self, **kwargs):
        session = kwargs.get("session", None)
        pk = kwargs.get("id", None)
        if session is None or pk is None:
            return False
        try:
            value = {k: self._clean_value(kwargs[k]) 
                    for k in self._filter_value(kwargs)}
            edit_obj = session.query(self._model).filter_by(id=pk)
            edit_obj.update(value)
            return edit_obj
        except Exception as e:
            logger.error("修改%s出错. %s, %s" % (self._model.__tablename__, e, kwargs))
            return False

    def delete_item(self, **kwargs):
        session = kwargs.get("session", None)
        if session is None:
            return False
        try:
            filter_obj = session.query(self._model)
            pk = kwargs.get("id", None)
            if pk is not None:
                filter_obj.filter_by(id=pk).delete()
            else:
                value = {k: self._clean_value(kwargs[k]) for k in self._filter_value(kwargs)}
                filter_obj = filter_obj.filter_by(**value)
                kv = kwargs.get("like", None)
                if kv is not None:
                    k, v = kv.split("^")
                    filter_obj = filter_obj.filter(getattr(self._model, k).like(f"%{v}%"))
                id_list = kwargs.get("id_list", None)
                if id_list is not None:
                    filter_obj = filter_obj.filter(getattr(self._model, "id").in_(id_list))
                filter_obj.delete()
            return True
        except Exception as e:
            logger.error("删除%s出错. %s, %s" % (self._model.__tablename__, e, kwargs))
            return False

    def id_match(self, session, input, match_key, attribute_list=None):
        # attribute_list 
        # [
        #   (当前存在的属性，新建的属性),
        #   当前存在的属性，默认把当前属性名字填充到新建属性里面
        # ]
        if session is None or attribute_list is None:
            return False
        if not isinstance(input, list):
            input = [input]
        id_list = [getattr(i, match_key) for i in input]
        item_list, _ = self.filter_item(session=session, id_list=id_list)
        id_dict = {getattr(k, "id"): k for k in item_list}
        for item in input:
            for i in attribute_list:
                if not isinstance(i, list) and not isinstance(i, tuple):
                    attribute, new_attribute = i, i
                else:
                    attribute, new_attribute = i[0], i[1]
                setattr(item, new_attribute, getattr(
                        id_dict.get(getattr(item, match_key), None),
                        attribute, None))
        return True

    def conf_match(self, input, attribute_list=None):
        # attribute_list 
        # [
        #   (当前存在的属性，新建的属性),
        #   当前存在的属性, 默认把当前属性名字加后缀_name 填充新建的属性
        # ]
        for i in attribute_list:
            if not isinstance(i, list) and not isinstance(i, tuple):
                i = (i, f"{i}_name")
        conf_dict = dict()
        for j in attribute_list:
            conf_dict[j[0]] = {i[0]: i[1]
                    for i in getattr(self._model, f"_conf_{j[0]}", [])}
        def _match(_input, _attribute_list):
            for i in _attribute_list:
                if hasattr(_input, i[0]) and not hasattr(_input, i[1]):
                    setattr(_input, i[1], conf_dict[i[0]].get(
                        getattr(_input, i[1]), None))
        if isinstance(input, list):
            for i in input:
                _match(i, attribute_list)
        else:
            _match(input, attribute_list)

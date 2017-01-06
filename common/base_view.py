#!/bin/env python
# -*- coding:utf8 -*-

import json
import time
import inspect

import tornado.web
import traceback
from tornado.escape import utf8

from .sqlalchemy_ctl import DBSession
from .mylog import logger
from . import error_msg
from . import utility

from conf import settings


class BaseView(tornado.web.RequestHandler):
    def initialize(self, controller_obj=None):
        # 每个请求有一个
        self._db_session = DBSession()
        self._user = None
        self._input = {}
        self._ret, self._msg = error_msg.SUCCESS
        self._data = {}
        self._resp_json = ""
        self._controller_obj = controller_obj

    def prepare(self, not_check_session_method=None, not_get_input_method=None):
        if not (not_check_session_method and
            self.request.method in not_check_session_method or
            self.check_session()):
            return self.response(error_msg.SESSION_ERROR)
        if not (not_get_input_method and self.request.method in not_get_input_method):
            self.__get_all_arguments()
        if not isinstance(self._input, dict):
            return self.response(error_msg.PARAMS_ERROR)
        self._input["session"] = self._db_session

    def get(self,
            must_input=None,
            enable_input=None,
            disable_input=None,
            disable_output=None):
        if not self.check_input_arguments(must_input, enable_input, disable_input):
            return self.response(error_msg.PARAMS_ERROR)
        if self._controller_obj is not None:
            if self._do_get(disable_output):
                self._db_session.commit()
            else:
                self._db_session.rollback()
            return self.response()
        else:
            return self.response(error_msg.SERVER_ERROR)

    def _do_get(self, disable_output=None, transform_json=True):
        try:
            data, total = self._controller_obj.filter_item(**self._input)
            self._data["total"] = total
            if transform_json:
                self._data["list"] = utility.to_obj(data, without_fields=disable_output)
            else:
                self._data["list"] = data
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._ret, self._msg = error_msg.SERVER_ERROR
            logger.error("get method error: %s" % e)
            return False

    def post(self,
            must_input=None,
            enable_input=None,
            disable_input=None,
            disable_output=None):
        if not self.check_input_arguments(must_input, enable_input, disable_input):
            return self.response(error_msg.PARAMS_ERROR)
        if self._controller_obj is not None:
            try:
                if self._controller_obj.new_item(**self._input):
                    self._ret, self._msg = error_msg.SUCCESS
                    self._db_session.commit()
                else:
                    self._ret, self._msg = error_msg.SERVER_ERROR
                    self._db_session.rollback()
                    logger.error("post method error")
            except Exception as e:
                self._ret, self._msg = error_msg.SERVER_ERROR
                self._db_session.rollback()
                logger.error("post method error: %s" % e)
            return self.response()
        else:
            return self.response(error_msg.SERVER_ERROR)

    def put(self,
            must_input=None,
            enable_input=None,
            disable_input=None,
            disable_output=None):
        if not self.check_input_arguments(must_input, enable_input, disable_input):
            return self.response(error_msg.PARAMS_ERROR)
        if self._controller_obj is not None:
            try:
                if self._controller_obj.update_item(**self._input):
                    self._ret, self._msg = error_msg.SUCCESS
                    self._db_session.commit()
                else:
                    self._ret, self._msg = error_msg.SERVER_ERROR
                    self._db_session.rollback()
                    logger.error("put method error")
            except Exception as e:
                self._ret, self._msg = error_msg.SERVER_ERROR
                self._db_session.rollback()
                logger.error("put method error: %s" % e)
            return self.response()
        else:
            return self.response(error_msg.SERVER_ERROR)

    def delete(self,
            must_input=None,
            enable_input=None,
            disable_input=None,
            disable_output=None):
        if not self.check_input_arguments(must_input, enable_input, disable_input):
            return self.response(error_msg.PARAMS_ERROR)
        if self._controller_obj is not None:
            try:
                if self._controller_obj.delete_item(**self._input):
                    self._ret, self._msg = error_msg.SUCCESS
                    self._db_session.commit()
                else:
                    self._ret, self._msg = error_msg.SERVER_ERROR
                    self._db_session.rollback()
                    logger.error("delete method error")
            except Exception as e:
                self._ret, self._msg = error_msg.SERVER_ERROR
                self._db_session.rollback()
                logger.error("delete method error: %s" % e)
            return self.response()
        else:
            return self.response(error_msg.SERVER_ERROR)

    def generate_session(self, id, type):
        plain_token = ("%s_%s_%s_dianfu" % (int(time.time()), id, type))
        return utility.encrypt(plain_token)

    def check_session(self):
        session = self.get_cookie("session_id", "")
        if not session:
            return False
        try:
            plain_token = utility.decrypt(session)
            plain_token_list = plain_token.split("_")
            create_time = plain_token_list[0]
            plain_id = plain_token_list[1]
            type = plain_token_list[2]
            if type == settings.ADMIN:
                timeout = settings.ADMIN_TOKEN_TIMEOUT
            else:
                timeout = settings.STUDENT_TOKEN_TIMEOUT
            if int(time.time()) - int(create_time) > timeout:
                return False
            if type == settings.ADMIN:
                self._user, _ = account_obj.filter_item(
                        session=self._db_session,
                        id=plain_id)
            else:
                self._user, _ = student_obj.filter_item(
                        session=self._db_session,
                        id=plain_id)
            return True
        except Exception as e:
            logger.error("decode error %s" % e)
            return False

    def response(self, msg=None, data=None):
        if msg:
            self._ret, self._msg = msg
        if data:
            self._data = data
        self._resp_json = json.dumps({
            "ret": self._ret,
            "msg": self._msg,
            "data": self._data
            })
        self.set_header('Content-Type', 'application/json')
        self.write(self._resp_json)
        self.finish()

    def on_finish(self):
        if self.request.files:
            logger.info("%s, ip: %s, query input: %s, body: file. "
                    "resp: %s. info: (%s), (%s), (%s), (%s)" %
                    (self.__class__.__name__,
                        self.request.remote_ip,
                        self.request.query_arguments,
                        self._resp_json,
                        self.get_status(),
                        (self.request.request_time()*1000), 
                        self.request.full_url(),
                        self.request.method))
        else:
            logger.info("%s, ip: %s, query input: %s, body: %s. "
                    "resp: %s. info: (%s), (%s), (%s), (%s)" %
                    (self.__class__.__name__,
                        self.request.remote_ip,
                        self.request.query_arguments,
                        self.request.body,
                        self._resp_json,
                        self.get_status(),
                        (self.request.request_time()*1000), 
                        self.request.full_url(),
                        self.request.method))
        self._db_session.close()

    def write_error(self, status_code, **kwargs):
        self._db_session.rollback()
        if "exc_info" in kwargs:
            logger.error("%s" % "".join(
                traceback.format_exception(*kwargs["exc_info"])))
        self.set_status(200, "OK")
        return self.response(error_msg.SERVER_ERROR, "error")

    def check_input_arguments(self,
            must_input=None,
            enable_input=None,
            disable_input=None):
        if must_input is None and enable_input is None and disable_input is None:
            return True
        s = set(self._input.keys())
        if must_input is not None:
            if not set(must_input) <= s:
                return False
        if enable_input is not None:
            y = set(enable_input)
            if not y <= s:
                return False
            s = y
        if disable_input is not None:
            s = s - set(disable_input)
        if enable_input is not None or disable_input is not None:
            self._input = {i: self._input.get(i, None) for i in s}
        return True

    def set_input_argument(self, key, value):
        self._input[key] = value

    def __get_all_arguments(self):
        if self.request.method == "GET":
            self._input = {i: self.get_query_argument(i) 
                    for i in self.request.query_arguments.keys()}
        else:
            try:
                if self.headers.get("Content-Type", "").startswith("application/json"):
                    self._input = json.loads(self.request.body)
                else:
                    self._input = {i: self.get_body_argument(i, None)
                            for i in self.request.body_arguments.keys()}
            except Exception as e:
                self._input = {}

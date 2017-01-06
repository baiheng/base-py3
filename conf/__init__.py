# -*-coding:utf-8-*-

import os
from . import settings_production
from . import settings_local

SETTINGS = os.environ.get('SETTINGS', '')

if SETTINGS == "PRODUCTION":
    settings = settings_production.BaseConfig()
else:
    settings = settings_local.LocalConfig()

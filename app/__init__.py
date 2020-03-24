# -*- coding: utf-8 -*-

import os

from emmett import App
from emmett.cache import Cache, RamCache
from emmett_haml import Haml
# from emmett_sentry import Sentry

app = App(__name__)

# app.config.static_version = '0.1.0'
# app.config.static_version_urls = True
app.config.url_default_namespace = "main"
app.config_from_yaml('version.yml', 'emmett_src')
app.config.Haml.set_as_default = True
app.config.Haml.auto_reload = True
app.config.templates_auto_reload = True
app.config.Sentry.dsn = os.environ.get('SENTRY_DSN', '')

app.use_extension(Haml)
# app.use_extension(Sentry)

cache = Cache(ram=RamCache())

from . import controllers

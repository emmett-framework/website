import os

from emmett import App
from emmett.cache import Cache, RamCache
from emmett_haml import Haml
from emmett_sentry import Sentry

app = App(__name__)

app.config_from_yaml('version.yml', 'emmett_src')
app.config.url_default_namespace = "main"
app.config.private_hostname = os.environ.get('PRIVATE_HOSTNAME', 'localhost')
app.config.Haml.set_as_default = True
app.config.Sentry.dsn = os.environ.get('SENTRY_DSN', '')

app.use_extension(Haml)
app.use_extension(Sentry)

cache = Cache(ram=RamCache())

from . import controllers

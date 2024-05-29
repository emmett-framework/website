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
app.config.Sentry.environment = os.environ.get('ENVIRONMENT', 'development')
app.config.Sentry.dsn = os.environ.get('SENTRY_DSN', '')
app.config.Sentry.release = os.environ.get('RELEASE', 'latest')
app.config.Sentry.enable_tracing = os.environ.get('SENTRY_TRACING') == 'true'
app.config.Sentry.tracing_sample_rate = 0.1
app.config.Sentry.tracing_exclude_routes = ['private.health']

app.use_extension(Haml)
app.use_extension(Sentry)

cache = Cache(ram=RamCache())

from . import controllers

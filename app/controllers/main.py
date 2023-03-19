from emmett import response

from .. import app, cache
from ..helpers.code_blocks import CodeBlocks

private = app.module(
    __name__, "private", hostname=f"{app.config.private_hostname}:8000"
)


@app.on_error(404)
async def error_404():
    response.content_type = 'text/html; charset=utf-8'
    return app.render_template("404.haml")


@app.on_error(500)
async def error_500():
    response.content_type = 'text/html; charset=utf-8'
    return app.render_template("500.haml")


@app.route("/", injectors=[CodeBlocks()])
@cache.response(query_params=False, language=False, duration=None)
async def index():
    return {"version": app.config.emmett_src.version}


@private.route("/_health", output="bytes")
async def health():
    return b"ok"

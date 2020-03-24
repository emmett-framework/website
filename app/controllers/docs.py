# -*- coding: utf-8 -*-

from emmett import abort, asis, redirect, url
from emmett.validators.process import Urlify

from .. import app, cache
from ..helpers.docs import (
    build_tree,
    get_chapter,
    get_html,
    get_latest_version,
    get_navigation,
    get_sections,
    get_versions,
    is_page
)

urlify = Urlify(keep_underscores=True)
docs = app.module(__name__, "docs", url_prefix="docs", template_folder="docs")


@docs.route("/")
async def index():
    redirect(url('.tree', 'latest'))


@docs.route("/<str:version>")
@cache.response(query_params=False, language=False, duration=60 * 60 * 24)
async def tree(version):
    if version == 'latest':
        redirect(url('.tree', get_latest_version()))
    if version not in get_versions():
        redirect(url('.page', 'latest'))
    doctree = await build_tree(version)
    if not doctree:
        abort(404)
    pages = []
    for title, name, subtree, sections in doctree:
        u = url('.page', [version, name])
        subs = []
        if subtree:
            for subtitle, subname, _, subsections in subtree:
                subs.append(
                    (subtitle, url('.page', [version, name, subname]))
                )
        else:
            for section in sections:
                slug = urlify(section)[0]
                subs.append((section, u + "#" + slug))
        pages.append((title, u, subs))
    return {'tree': pages, 'version': version, 'versions': get_versions()}


@docs.route("/<str:version>/<str:key>(/<str:subkey>)?")
@cache.response(query_params=False, language=False, duration=60 * 30)
async def page(version, key, subkey):
    if version == 'latest':
        vlast = get_latest_version()
        pargs = [vlast, key]
        if subkey:
            pargs.append(subkey)
        redirect(url('.page', pargs))
    if subkey:
        requested_page = subkey
        parent = key
    else:
        requested_page = key
        parent = None
    if not is_page(version, requested_page, parent):
        abort(404)
    sections = []
    for section in await get_sections(version, requested_page, parent):
        sections.append((section, urlify(section)[0]))
    body = asis(await get_html(version, requested_page, parent))
    title = await get_chapter(version, requested_page, parent)
    prev, after = await get_navigation(version, requested_page, parent)
    return {
        'title': title,
        'body': body,
        'sections': sections,
        'prev': prev,
        'after': after,
        'version': version,
        'versions': get_versions()
    }

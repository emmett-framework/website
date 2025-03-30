import os

from emmett_core._io import loop_open_file
from yaml import SafeLoader as ymlLoader, load as ymlload
from markdown2 import markdown

from .. import app, cache

_docs_path = os.path.join(app.root_path, 'docs')


def _build_filepath(version, name, parent=None):
    args = [_docs_path, version, name + ".md"]
    if parent:
        args.insert(2, parent)
    return os.path.join(*args)


@cache('docs_versions', duration=None)
def get_versions():
    versions = []
    for name in os.listdir(_docs_path):
        if os.path.isdir(os.path.join(_docs_path, name)):
            versions.append(name)
    return sorted(versions, reverse=True)


@cache('docs_lastv', duration=None)
def get_latest_version():
    latest_version = max([
        float(".".join(v.split(".")[:-1])) for v in get_versions()
    ])
    return f"{latest_version}.x"


def is_page(version, name, parent=None):
    path = _build_filepath(version, name, parent)
    return os.path.exists(path)


@cache('docs_content', duration=60 * 60 * 24)
async def _get_content(version, name, parent=None):
    async with loop_open_file(
        _build_filepath(version, name, parent), 'rt'
    ) as f:
        data = await f.read()
    return data


@cache('docs_lines', duration=60 * 60 * 24)
async def _get_lines(version, name, parent=None):
    return (await _get_content(version, name, parent)).splitlines()


async def get_chapter(version, name, parent=None):
    lines = await _get_lines(version, name, parent)
    chapter = name
    for i in range(0, len(lines)):
        if lines[i].startswith("==="):
            chapter = lines[i - 1]
            break
    return chapter


async def get_sections(version, name, parent=None):
    lines = await _get_lines(version, name, parent)
    sections = []
    for i in range(0, len(lines)):
        if lines[i].startswith("---"):
            sections.append(lines[i - 1].replace("\\", ""))
    return sections


async def _get_subpages(version, parent, pages):
    rv = []
    for page in pages:
        title = await get_chapter(version, page, parent)
        sections = await get_sections(version, page, parent)
        rv.append((title, page, [], sections))
    return rv


@cache('docs_tree', duration=None)
async def build_tree(version):
    folder = os.path.join(_docs_path, version)
    if not os.path.exists(folder):
        return None
    with open(os.path.join(folder, 'tree.yml')) as f:
        tree = ymlload(f, Loader=ymlLoader)
    complete_tree = []
    subpaged = []
    for name in tree:
        if isinstance(name, dict):
            rname = list(name)[0]
            subpaged.append(rname)
            ch_name = await get_chapter(version, rname)
            sub_tree = await _get_subpages(version, rname, name[rname])
            complete_tree.append((ch_name, rname, sub_tree, []))
        else:
            if name in subpaged:
                continue
            ch_name = await get_chapter(version, name)
            sub_tree = await get_sections(version, name)
            complete_tree.append((ch_name, name, [], sub_tree))
    return complete_tree


async def get_html(version, name, parent=None):
    text = await _get_content(version, name, parent)
    if text is None:
        return text
    extras = ['tables', 'fenced-code-blocks', 'header-ids']
    return markdown(text, extras=extras)


def _navigation_tree_pos(tree, pname):
    rv = None
    for i in range(0, len(tree)):
        if tree[i][1] == pname:
            rv = i
            break
    return rv


def _navigation_data(version, tree_obj, parent=None):
    if tree_obj is None:
        return tree_obj
    return tree_obj[0], tree_obj[1], parent, version


def _tree_nav(version, tree, page, subtree=True):
    prev, after = None, None
    index = _navigation_tree_pos(tree, page)
    if index > 0:
        prev = tree[index - 1]
    if index < len(tree) - 1:
        after = tree[index + 1]
    current_parent = None
    if subtree and tree[index][2]:
        after = tree[index][2][0]
        current_parent = page
    return (
        _navigation_data(version, prev),
        _navigation_data(version, after, current_parent)
    )


async def get_navigation(version, page, parent=None):
    prev, after = None, None
    tree = await build_tree(version)
    if not parent:
        prev, after = _tree_nav(version, tree, page)
    else:
        pindex = _navigation_tree_pos(tree, parent)
        subtree = tree[pindex]
        index = _navigation_tree_pos(subtree[2], page)
        if index > 0:
            prev = _navigation_data(version, subtree[2][index - 1], parent)
        else:
            prev = _navigation_data(version, tree[pindex])
        if index < len(subtree[2]) - 1:
            after = _navigation_data(version, subtree[2][index + 1], parent)
        else:
            after = _tree_nav(version, tree, parent, False)[1]
    return prev, after

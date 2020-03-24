# -*- coding: utf-8 -*-

import os
import shutil

from subprocess import Popen, PIPE
from yaml import SafeLoader as ymlLoader, load as ymlload

cur_path = os.path.dirname(os.path.realpath(__file__))
tmp_path = os.path.join(cur_path, 'tmp')
dist_path = os.path.join(cur_path, 'dist')


class GitGetter(object):
    def __init__(self, repo, store_in):
        self.repo = repo
        self.storage = store_in
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)

    @property
    def folder(self):
        return os.path.join(tmp_path, self.storage)

    def clone(self):
        os.chdir(tmp_path)
        Popen(['git', 'clone', self.repo, self.storage]).wait()

    def tags(self):
        os.chdir(self.folder)
        return set(
            Popen(
                ['git', 'tag'], stdout=PIPE
            ).communicate()[0].decode('utf8').splitlines()
        )


def update_version():
    dest_path = os.path.join(dist_path, 'version')
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    os.mkdir(dest_path)
    os.chdir(os.path.join(tmp_path, "emtsrc"))
    n, codename = "2.0", "Archimedes"
    # Popen(["git", "checkout", "release"]).wait()
    # changelog = os.path.join(tmp_path, "emtsrc", "CHANGES.md")
    # with open(changelog, "r") as f:
    #     lines = f.readlines()
    # for idx, line in enumerate(lines):
    #     if line.startswith("---"):
    #         if lines[idx - 1].startswith("Version"):
    #             n = lines[idx - 1].split("Version ")[1].replace('\n', '')
    #             codename = lines[idx + 2].split(", codename ")[1].replace('\n', '')
    #             break
    with open(os.path.join(dest_path, 'version.yml'), 'w') as f:
        f.write(f'version: "{n} {codename}"')


def update_docs():
    dest_path = os.path.join(dist_path, 'docs')
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    os.mkdir(dest_path)
    with open(os.path.join(cur_path, 'versions.yml')) as f:
        tree = ymlload(f, Loader=ymlLoader)
    for label, git_target in tree['versions'].items():
        docs_path = os.path.join(dest_path, label)
        os.mkdir(docs_path)
        os.chdir(os.path.join(tmp_path, "emtsrc"))
        Popen(["git", "checkout", git_target]).wait()
        src_path = os.path.join(tmp_path, "emtsrc", "docs")
        for name in os.listdir(src_path):
            if os.path.isdir(os.path.join(src_path, name)):
                shutil.copytree(
                    os.path.join(src_path, name),
                    os.path.join(docs_path, name))
            else:
                shutil.copy2(os.path.join(src_path, name), docs_path)


def build():
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    if not os.path.exists(dist_path):
        os.mkdir(dist_path)
    getter = GitGetter("https://github.com/emmett-framework/emmett.git", "emtsrc")
    getter.clone()
    update_version()
    update_docs()


if __name__ == '__main__':
    build()

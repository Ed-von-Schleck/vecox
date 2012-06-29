# -*- coding: utf-8 -*-

import glob
import os
import os.path
import datetime
import zlib

from src import vecox

vecox_DIRNAME = ".vecox"

@vecox.register("backend", "file")
class FileBackend(object):
    def __init__(self):
        self._abs_root_directory_cache = None

    def init(self):
        vecox_abs_path = self._abs_root_directory()
        if vecox_abs_path is not None:
            raise vecox.vecoxError("vecox already initialized in " + vecox_abs_path)
        try:
            os.mkdir(".vecox")
        except OSError:
            raise vecox.vecoxError("Unable to create .vecox directory")
        else:
            print("Initialized vecox")

    def save(self, filenames, filetype, message):
        vecox_root_path = self._abs_root_directory()
        if vecox_root_path is None:
            raise vecox.vecoxError("vecox not initialized")

        rel_vecox_fileset = self._rel_vecox_fileset(filenames)

        for filename in rel_vecox_fileset:
            html = os.path.splitext(filename)[1] in {".html", "htm"} or filetype == "html"

            hsh = None

            # write partials
            for hsh, content in vecox.parse(filename, html=html):
                with open(os.path.join(vecox_root_path, vecox_DIRNAME, hsh), "wb") as hshfile:
                    hshfile.write(content)

            # write commit
            try:
                with open(os.path.join(vecox_root_path, vecox_DIRNAME, filename), "r") as vecoxfile:
                    last_hsh = vecoxfile.read()
            except IOError:
                last_hsh = ""

            commit_hsh, commit = vecox.generate_commit(hsh, os.stat(filename).st_mtime, last_hsh, html, message)
            with open(os.path.join(vecox_root_path, vecox_DIRNAME, commit_hsh), "wb") as commitfile:
                commitfile.write(commit)

            # write pointer to commit hash
            with open(os.path.join(vecox_root_path, vecox_DIRNAME, filename), "w") as vecoxfile:
                vecoxfile.write(commit_hsh)
            print("saved as revision:", commit_hsh)

    def history(self, filenames):
        vecox_root_path = self._abs_root_directory()
        if vecox_root_path is None:
            raise vecox.vecoxError("vecox not initialized")

        rel_vecox_fileset = self._rel_vecox_fileset(filenames)

        if not rel_vecox_fileset:
            raise vecox.vecoxError("No matching filename")

        for filename in rel_vecox_fileset:
            print("\n", filename, sep="")
            print("-" * len(filename))
            with open(os.path.join(vecox_root_path, vecox_DIRNAME, filename)) as openfile:
                commit_hsh = openfile.read()
            with open(os.path.join(vecox_root_path, vecox_DIRNAME, commit_hsh)) as commitfile:
                last_hsh = self._print_commit(commit_hsh, commitfile)
                while last_hsh:
                    with open(os.path.join(vecox_root_path, vecox_DIRNAME, last_hsh)) as previous_file:
                        last_hsh = self._print_commit(last_hsh, previous_file)

    def revision(self, filename, commit_hsh_prefix, force):
        vecox_root_path = self._abs_root_directory()
        commit_hsh_paths = glob.glob(os.path.join(vecox_root_path, vecox_DIRNAME, commit_hsh_prefix) + "*")

        # get last modified
        if not force:
            mtime_file = os.stat(filename).st_mtime
            with open(os.path.join(vecox_root_path, vecox_DIRNAME, filename)) as vecoxfile:
                recent_commit_hsh = vecoxfile.readline().rstrip()
            with open(os.path.join(vecox_root_path, vecox_DIRNAME, recent_commit_hsh)) as recent_commit_file:
                mtime_commit = recent_commit_file.readline().rstrip()
            if str(mtime_file) != mtime_commit:
                raise vecox.vecoxError("Current version of " + filename + " not saved (use '--force' to do it anyways)")

        if not commit_hsh_paths:
            raise vecox.vecoxError("No matching revision")
        if len(commit_hsh_paths) > 1:
            raise vecox.vecoxError("More than one matching revision")
        commit_hsh_path = commit_hsh_paths[0]

        def get_raw_content(hsh):
            with open(os.path.join(vecox_root_path, vecox_DIRNAME, hsh), "rb") as hshfile:
                return hshfile.read()

        with open(commit_hsh_path) as openfile:
            next(openfile)
            root_hsh = openfile.readline().rstrip()
            html = openfile.readline().rstrip() == "html"

        with open(filename, "wb") as openfile:
            openfile.write(vecox.reconstruct(root_hsh, html, get_raw_content))

    def _abs_root_directory(self):
        #TODO: replace with getter property?
        if self._abs_root_directory_cache is not None:
            return self._abs_root_directory_cache
        path = os.getcwd()
        while True:
            if os.path.exists(vecox_DIRNAME) and os.path.isdir(vecox_DIRNAME):
                self._abs_root_directory_cache = path
                return path
            if path == os.path.dirname(path):
                return None
            path = os.path.dirname(path)

    def _rel_vecox_fileset(self, filenames):
        vecox_root_path = self._abs_root_directory()

        #TODO: maybe a set comprehension?
        fileset = set()
        for fileglob in filenames:
            fileset |= set(glob.glob(fileglob))

        return {os.path.relpath(os.path.abspath(filename), vecox_root_path) for filename in fileset}

    def _print_commit(self, hsh, openfile):
        print("commit:      ", hsh)
        print("datetime:    ", datetime.datetime.fromtimestamp(float(openfile.readline())))
        print("root element:", openfile.readline().rstrip())
        last_hsh = openfile.readline().rstrip()
        #print("last commit: ", last_hsh, end="")
        print("type:        ", openfile.readline().rstrip())
        print("message:     ", openfile.readline())
        print()
        return last_hsh

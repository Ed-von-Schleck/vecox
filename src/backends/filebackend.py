# -*- coding: utf-8 -*-

import glob
import os
import os.path
import datetime
import zlib

from src import vecoh

VECOH_DIRNAME = ".vecoh"

@vecoh.register("backend", "file")
class FileBackend(object):
    def __init__(self):
        self._abs_root_directory_cache = None

    def init(self):
        vecoh_abs_path = self._abs_root_directory()
        if vecoh_abs_path is not None:
            raise vecoh.VecohError("vecoh already initialized in " + vecoh_abs_path)
        try:
            os.mkdir(".vecoh")
        except OSError:
            raise vecoh.VecohError("Unable to create .vecoh directory")
        else:
            print("Initialized vecoh")

    def save(self, filenames, filetype, message):
        vecoh_root_path = self._abs_root_directory()
        if vecoh_root_path is None:
            raise vecoh.VecohError("vecoh not initialized")

        rel_vecoh_fileset = self._rel_vecoh_fileset(filenames)

        for filename in rel_vecoh_fileset:
            html = os.path.splitext(filename)[1] in {".html", "htm"} or filetype == "html"

            hsh = None

            # write partials
            for hsh, content in vecoh.parse(filename, html=html):
                with open(os.path.join(vecoh_root_path, VECOH_DIRNAME, hsh), "wb") as hshfile:
                    hshfile.write(content)

            # write commit
            try:
                with open(os.path.join(vecoh_root_path, VECOH_DIRNAME, filename), "r") as vecohfile:
                    last_hsh = vecohfile.read()
            except IOError:
                last_hsh = ""

            commit_hsh, commit = vecoh.generate_commit(hsh, os.stat(filename).st_mtime, last_hsh, html, message)
            with open(os.path.join(vecoh_root_path, VECOH_DIRNAME, commit_hsh), "wb") as commitfile:
                commitfile.write(commit)

            # write pointer to commit hash
            with open(os.path.join(vecoh_root_path, VECOH_DIRNAME, filename), "w") as vecohfile:
                vecohfile.write(commit_hsh)

    def history(self, filenames):
        vecoh_root_path = self._abs_root_directory()
        if vecoh_root_path is None:
            raise vecoh.VecohError("vecoh not initialized")

        rel_vecoh_fileset = self._rel_vecoh_fileset(filenames)

        if not rel_vecoh_fileset:
            raise vecoh.VecohError("No matching filename")

        for filename in rel_vecoh_fileset:
            print("\n", filename, sep="")
            print("-" * len(filename))
            with open(os.path.join(vecoh_root_path, VECOH_DIRNAME, filename)) as openfile:
                commit_hsh = openfile.read()
            with open(os.path.join(vecoh_root_path, VECOH_DIRNAME, commit_hsh)) as commitfile:
                last_hsh = self._print_commit(commit_hsh, commitfile)
                while last_hsh:
                    with open(os.path.join(vecoh_root_path, VECOH_DIRNAME, last_hsh)) as previous_file:
                        last_hsh = self._print_commit(last_hsh, previous_file)

    def revision(self, filename, commit_hsh_prefix, force):
        vecoh_root_path = self._abs_root_directory()
        commit_hsh_paths = glob.glob(os.path.join(vecoh_root_path, VECOH_DIRNAME, commit_hsh_prefix) + "*")

        # get last modified
        if not force:
            mtime_file = os.stat(filename).st_mtime
            with open(os.path.join(vecoh_root_path, VECOH_DIRNAME, filename)) as vecohfile:
                recent_commit_hsh = vecohfile.readline().rstrip()
            with open(os.path.join(vecoh_root_path, VECOH_DIRNAME, recent_commit_hsh)) as recent_commit_file:
                mtime_commit = recent_commit_file.readline().rstrip()
            if str(mtime_file) != mtime_commit:
                raise vecoh.VecohError("Current version of " + filename + " not saved (use '--force' to do it anyways)")

        if not commit_hsh_paths:
            raise vecoh.VecohError("No matching revision")
        if len(commit_hsh_paths) > 1:
            raise vecoh.VecohError("More than one matching revision")
        commit_hsh_path = commit_hsh_paths[0]

        def get_raw_content(hsh):
            with open(os.path.join(vecoh_root_path, VECOH_DIRNAME, hsh), "rb") as hshfile:
                return hshfile.read()

        with open(commit_hsh_path) as openfile:
            next(openfile)
            root_hsh = openfile.readline().rstrip()
            html = openfile.readline().rstrip() == "html"

        with open(filename, "wb") as openfile:
            openfile.write(vecoh.reconstruct(root_hsh, html, get_raw_content))

    def _abs_root_directory(self):
        #TODO: replace with getter property?
        if self._abs_root_directory_cache is not None:
            return self._abs_root_directory_cache
        path = os.getcwd()
        while True:
            if os.path.exists(VECOH_DIRNAME) and os.path.isdir(VECOH_DIRNAME):
                self._abs_root_directory_cache = path
                return path
            if path == os.path.dirname(path):
                return None
            path = os.path.dirname(path)

    def _rel_vecoh_fileset(self, filenames):
        vecoh_root_path = self._abs_root_directory()

        #TODO: maybe a set comprehension?
        fileset = set()
        for fileglob in filenames:
            fileset |= set(glob.glob(fileglob))

        return {os.path.relpath(os.path.abspath(filename), vecoh_root_path) for filename in fileset}

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

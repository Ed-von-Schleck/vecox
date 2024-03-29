# -*- coding: utf-8 -*-

import pkgutil

from src import vecox
from src import backends

def save(args):
    Backend = vecox.registry_get("backend", args.backend)
    Backend().save(args.filenames, args.filetype, args.message)

def init(args):
    Backend = vecox.registry_get("backend", args.backend)
    Backend().init()

def history(args):
    Backend = vecox.registry_get("backend", args.backend)
    Backend().history(args.filenames)

def revision(args):
    Backend = vecox.registry_get("backend", args.backend)
    Backend().revision(args.filename, args.hash, args.force)

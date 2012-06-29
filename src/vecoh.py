# -*- coding: utf-8 -*-

from hashlib import sha1
import datetime
import io

from lxml import etree

HASH_PREFIX = "sha1_"

_registry = {}

def parse(xmlfile, html=False):
    context = etree.iterparse(xmlfile, html=html)
    for action, element in context:
        string = etree.tostring(element, encoding="UTF-8")
        hsh = sha1(string).hexdigest()

        parent = element.getparent()
        if parent is not None:
            yield hsh, string
            parent.replace(element, etree.Element(HASH_PREFIX + hsh))

    tree = context.root.getroottree()
    yield hsh, etree.tostring(tree, encoding="UTF-8")

def generate_commit(root_hsh, mtime, last_hsh, html, message):
    commit = [str(mtime)]
    commit.append(root_hsh)
    commit.append(last_hsh)
    commit.append("html" if html else "xml")
    commit.append(message)
    scommit = bytes("\n".join(commit), encoding="utf-8")
    return sha1(scommit).hexdigest(), scommit

def reconstruct(root_hsh, html, get_func):
    parser = etree.HTMLParser() if html else etree.XMLParser()
    root = etree.fromstring(get_func(root_hsh), parser=parser)
    def recursive_walk(element):
        for child in element.iter():
            if child.tag[0:5] == HASH_PREFIX:
                raw_content = get_func(child.tag[5:])
                # tail handling
                #TODO: make that more efficient
                raw_element, sep, tail = raw_content.rpartition(b">")
                new_child = etree.fromstring(raw_element + sep)
                new_child.tail = tail
                recursive_walk(new_child)
                element.replace(child, new_child)

    recursive_walk(root)
    return etree.tostring(root.getroottree())

def register(storage, name):
    if _registry.get(storage) is None:
        _registry[storage] = {}
    def wrap(cls):
        _registry[storage][name] = cls
        return cls
    return wrap

def registry_get(storage, name=None):
    if name is None:
        return _registry[storage]
    else:
        return _registry[storage][name]

class VecohError(Exception):
    def __init__(self, message):
        self.message = message

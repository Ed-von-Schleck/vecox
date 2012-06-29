#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  simple_example.py
#
#  Copyright 2012 Christian Schramm <christian.h.m.schramm@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import io

from src import vecox

html = b"""<!doctype html>
<html>
<head>
    <title>test</title>
</head>
<body>
    <p>some <b>bold</b> content</p>
    <p>some more<span>with an inline span</span> hopefully parsed right.</p>
</body>
</html>
"""

xml = b"""<?xml version="1.0" encoding="UTF-8" ?>
<html>
<head>
    <title>test</title>
</head>
<body>
    <p>some <b>bold</b> content</p>
    <p>some more<span>with an inline span</span> hopefully parsed right.</p>
</body>
</html>
"""


for hsh, string in vecox.parse(io.BytesIO(html), html=True):
    print(hsh, string)


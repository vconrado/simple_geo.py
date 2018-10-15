# -*- coding: utf-8 -*-
#
#   Copyright (C) 2017 National Institute For Space Research (INPE) - Brazil.
#
#  This file is part of simple_geo.py toolkit.
#
#  simple_geo.py toolkit is free software: you can
#  redistribute it and/or modify it under the terms of the
#  GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License,
#  or (at your option) any later version.
#
#  simple_geo.py toolkit is distributed in the hope that
#  it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with simple_geo.py toolkit. See LICENSE. If not, write to
#  e-sensing team at <esensing-team@dpi.inpe.br>.
#

from SimpleGeo import SimpleGeo
from SimpleGeo import Predicates as pre

# Trying to import user and password data
try:
    from auth_data import *
except ImportError:
    # or setting auth data
    auth = ("user", "password")

s = SimpleGeo(wfs="http://eodb.dpi.inpe.br/geoserver/",
              debug=False, cache=False, auth=auth)

for feature in s.features()['features']:
    print(feature)
    f = s.feature(feature).max_features(20)
    print(f.describe())
    print(f.get())

f = s.feature("inpe_obt:prodes_amazonia")\
    .max_features(20) \
    .filter(pre.OR(
        pre.EQ("classe", "Floresta"),
        pre.EQ("classe", "Pasto Sujo")
    )) \
    .attributes(["classe", "uf"]) \
    .sort_by("uf")

print(f.get())

print("Done !!!")

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


class Coverage:
    def __init__(self, simple_geo, name, **kwargs):
        """Create Coverage object.
        Args:
            name(str): Coverage Name
            **kwargs: Keyword arguments:
                debug (boolean, optional): enable debug messages
        """
        # if type(simple_geo) is not SimpleGeo:
        #     raise AttributeError('simple_geo must be a SimpleGeo object')

        if type(name) is not str:
            raise AttributeError('name must be a string')

        if len(name) < 1:
            raise AttributeError('invalid Feature name')

        self.__simple_geo = simple_geo
        self.attr = {
            'name': name,
            'attributes': []
        }

    def __getitem__(self, key):
        if key in self.attr:
            return self.attr[key]

    def attributes(self, attr):
        if type(attr) is str:
            attr = [attr, ]
        elif type(attr) not in [tuple, list]:
            raise AttributeError('attributes must be a list, tuple or string')
        self.attr['attributes'] = attr
        return self

    def get(self):
        return self.__simple_geo.get(self)

    def describe(self):
        return self.__simple_geo.describe_coverage(self.attr['name'])

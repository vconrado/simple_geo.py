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


class Feature:
    def __init__(self, simple_geo, name, **kwargs):
        """Create Feature object.
        Args:
            name(str): Feature Name
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
        self._name = name
        self._attributes = []
        self._filter = ""
        self._max_features = []
        self._sort_by = []

    def attributes(self, attr):
        if type(attr) is str:
            attr = [attr, ]
        elif type(attr) not in [tuple, list]:
            raise AttributeError('attributes must be a list, tuple or string')
        self._attributes = attr
        return self

    def filter(self, ftr):
        if type(ftr) is not str:
            raise AttributeError('attributes must a string')
        self._filter = ftr
        return self

    def max_features(self, max_ft):
        if max_ft < 1:
            raise AttributeError('max_features must be greater than 0')
        self._max_features = max_ft
        return self

    def sort_by(self, sb):
        if type(sb) is str:
            sb = [sb, ]
        elif type(sb) not in [tuple, list]:
            raise AttributeError('attributes must be a list, tuple or string')
        self._sort_by = sb
        return self

    def get(self):
        return self.__simple_geo.get(self)

    def describe(self):
        return self.__simple_geo.describe_feature(self._name)

    def __str__(self):
        str_obj = "Feature[\n"
        str_obj += "\tname: {}\n".format(self._name)
        str_obj += "\tmax_feature: {}\n".format(self._max_features)
        str_obj += "\tsort_by: {}\n".format(",".join(self._sort_by))
        str_obj += "\tattributes: {}\n".format(",".join(self._attributes))
        str_obj += "\tfilter: {}\n".format(self._filter)
        str_obj += "]\n"
        return str_obj

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

from Feature import Feature
from wtss import wtss
from wfs import wfs
import pandas as pd
from geopandas import GeoDataFrame

try:
    # For Python 3.0 and later
    from urllib.request import quote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import quote


class SimpleGeo:
    def __init__(self, **kwargs):
        """Create wfs and wtss clients attached to given host addresses.
        Args:
            wfs (str): WFS server URL
            wtss (str): WTSS server URL
            debug (boolean, optional): enable debug messages
        """

        invalid_parameters = set(kwargs) - {"debug", "wfs", "wtss", "cache", "cache_dir"}
        if invalid_parameters:
            raise AttributeError('invalid parameter(s): {}'.format(invalid_parameters))

        self.__debug = False
        if 'debug' in kwargs:
            if not type(kwargs['debug']) is bool:
                raise AttributeError('debug must be a boolean')
            self.__debug = kwargs['debug']

        self.__cache = False
        if 'cache' in kwargs:
            if not type(kwargs['cache']) is bool:
                raise AttributeError('cache must be a boolean')
            self.__cache = kwargs['cache']

        self.__cache_dir = "./.sgeo/cache"
        if 'cache_dir' in kwargs:
            if not type(kwargs['cache_dir']) is str:
                raise AttributeError('cache_dir must be a str')
            self.__cache_dir = kwargs['cache_dir']

        self.__wfs = None
        if type(kwargs['wfs'] is str):
            self.__wfs_server = kwargs['wfs']
            self.__wfs = wfs(kwargs['wfs'], debug=self.__debug)
        else:
            raise AttributeError('wfs must be a string')

        self.__wtss = None
        if type(kwargs['wtss'] is str):
            self.__wtss_server = kwargs['wtss']
            self.__wtss = wtss(kwargs['wtss'])
        else:
            raise AttributeError('wtss must be a string')

    def feature(self, name):
        return Feature(self, name)

    def get(self, resource):
        if resource.__class__.__name__ is "Feature":
            return self.__get_feature(resource)
        else:
            raise NotImplementedError("Not implemented")

    def __get_feature(self, feature):

        kargs = {"max_features": feature._max_features,
                 "attributes": feature._attributes,
                 "filter": feature._filter,
                 "sort_by": feature._sort_by}

        fc = self.__wfs.feature_collection(feature._name, **kargs)

        if len(fc['features']) == 0:
            geo_data = pd.DataFrame()
            geo_data.total_features = 0
        else:
            geo_data = pd.DataFrame(fc['features'])
            geo_data = GeoDataFrame(geo_data, geometry='geometry', crs=fc['crs'])
            geo_data.total_features = fc['total_features']
        return geo_data

class Operations:
    @staticmethod
    def AND(*arg):
        if len(arg) < 2:
            raise AttributeError('It is necessary at least 2 operators for AND operator')
        str_and = ""
        for a in arg:
            if str_and != "":
                str_and += "+AND+"
            str_and += "({})".format(a)
        return str_and

    @staticmethod
    def OR(*arg):
        if len(arg) < 2:
            raise AttributeError('It is necessary at least 2 operators for OR operator')
        str_or = ""
        for a in arg:
            if str_or != "":
                str_or += "+OR+"
            str_or += "({})".format(a)
        return str_or

    @staticmethod
    def ASC(op1):
        return "({} A)".format(op1)

    @staticmethod
    def DESC(op1):
        return "({} D)".format(op1)

    @staticmethod
    def EQ(op1, op2):
        return "{}='{}'".format(op1, op2)

    @staticmethod
    def NE(op1, op2):
        return "{}!='{}'".format(op1, op2)

    @staticmethod
    def LT(op1, op2):
        return "{}<'{}'".format(op1, op2)

    @staticmethod
    def GT(op1, op2):
        return "{}>'{}'".format(op1, op2)

    @staticmethod
    def LE(op1, op2):
        return "{}<='{}'".format(op1, op2)

    @staticmethod
    def GE(op1, op2):
        return "{}>='{}'".format(op1, op2)

    @staticmethod
    def BT(op1, op2, op3):
        return "{}>='{}'".format(op1, op2)

    @staticmethod
    def WITHIN(wkt):
        return "WITHIN(#geom#, {})".format(wkt)

    @staticmethod
    def INTERSECTS(wkt):
        return "INTERSECTS(#geom#, {})".format(wkt)


        # spatial_op_dict = {
        #             'within': 'Within',
        #             'intersects': 'Intersects',
        #             'overlaps': 'Overlaps',
        #             'touches': 'Touches',
        #             'contain': 'Contains',
        #             'crosses': 'Crosses',
        #             'disjoint': 'Disjoint'
        #         }

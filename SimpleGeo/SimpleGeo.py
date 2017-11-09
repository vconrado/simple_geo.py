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
from Coverage import Coverage
from TimeSerie import TimeSerie
from wtss import wtss
from wfs import wfs
import pandas as pd
from geopandas import GeoDataFrame
import cPickle
import os
import hashlib
import json

try:
    # For Python 3.0 and later
    from urllib.request import quote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import quote

# encoding=utf8
import sys

stdout = sys.stdout
reload(sys)
sys.setdefaultencoding('utf8')
sys.stdout = stdout


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

    def features(self):
        return self.__wfs.list_features()

    def describe_feature(self, name):
        return self.__wfs.describe_feature(name)

    def coverage(self, name):
        return Coverage(self, name)

    def coverages(self):
        return self.__wtss.list_coverages()

    def describe_coverage(self, name):
        return self.__wtss.describe_coverage(name)

    def time_serie(self, coverage):
        return TimeSerie(self, coverage)

    def get(self, resource, **kwargs):
        if resource.__class__.__name__ is "Feature":
            return self.__get_feature(resource, **kwargs)
        elif resource.__class__.__name__ is "Coverage":
            return self.__get_coverage(resource, **kwargs)
        elif resource.__class__.__name__ is "TimeSerie":
            return self.__get_time_serie(resource, **kwargs)
        else:
            raise NotImplementedError("Not implemented")

    def __get_feature(self, feature, **kwargs):

        args = {"max_features": feature._max_features,
                "attributes": feature._attributes,
                "filter": feature._filter,
                "sort_by": feature._sort_by}

        fc = None
        if self.__cache:
            fc = self._get_cache(self.__wfs_server, "feature_collection", feature._name, args)
        if fc is None:
            fc = self.__wfs.feature_collection(feature._name, **args)
            if self.__cache:
                self._set_cache(self.__wfs_server, "feature_collection", feature._name, args, fc)

        if len(fc['features']) == 0:
            geo_data = pd.DataFrame()
            geo_data.total_features = 0
        else:
            geo_data = pd.DataFrame(fc['features'])
            geo_data = GeoDataFrame(geo_data, geometry='geometry', crs=fc['crs'])
            geo_data.total_features = fc['total_features']
        return geo_data

    def __get_time_serie(self, time_serie, **kwargs):

        # cv = self.__wtss.time_series(time_serie._coverage._name, time_serie._coverage._attributes, latitude,
        #                             longitude, time_serie._start_date, time_serie._end_date)

        coverage = time_serie._coverage._name
        attributes = time_serie._coverage._attributes
        latitude = kwargs['pos'].y
        longitude = kwargs['pos'].x
        start_date = time_serie._start_date
        end_date = time_serie._end_date

        if self.__wtss is None:
            raise AttributeError('wtss server is not defined')

        cv = None
        if self.__cache:
            args = {'attributes': attributes, 'latitude': latitude, 'longitude': longitude, 'start_date': start_date,
                    'end_date': end_date}
            cv = self._get_cache(self.__wtss_server, "time_serie", coverage, args)
        if cv is None:
            cv = self.__wtss.time_series(coverage, attributes, latitude, longitude, start_date, end_date)
            if self.__cache:
                self._set_cache(self.__wtss_server, "time_serie", coverage, args, cv)

        data = pd.DataFrame(cv.attributes, index=cv.timeline)
        data.total = len(cv.timeline)
        return data

    def __get_coverage(self, coverage, **kwargs):
        raise NotImplementedError("Not implemented")

    def _get_cache(self, server, resource_type, resource_name, kwargs):
        """ Try to get cached request"""
        hash_params = SimpleGeo._get_cache_hash(server, resource_type, resource_name, kwargs)
        file_path = "{}/{}/{}.pkl".format(self.__cache_dir, resource_type, hash_params)
        if os.path.isfile(file_path):
            if os.path.getsize(file_path) > 0:
                with open(file_path, 'rb') as handle:
                    if self.__debug:
                        print("Cache found !")
                    content = cPickle.load(handle)
                    return content
        if self.__debug:
            print("Cache not found !")
        return None

    def _set_cache(self, server, resource_type, resource_name, kwargs, content):
        """ Store a response on cache"""
        hash_params = SimpleGeo._get_cache_hash(server, resource_type, resource_name, kwargs)
        path_cache = "{}/{}".format(self.__cache_dir, resource_type)
        if not os.path.exists(path_cache):
            os.makedirs(path_cache)
        file_path = "{}/{}.pkl".format(path_cache, hash_params)
        with open(file_path, 'wb') as handle:
            cPickle.dump(content, handle, protocol=cPickle.HIGHEST_PROTOCOL)

    @staticmethod
    def _get_cache_hash(server, resource_type, resource_name, kwargs):
        """Creates an hash from request parameters"""
        params = "{}.{}.{}.{}".format(server, resource_type, resource_name, json.dumps(kwargs))
        return hashlib.sha256(params).hexdigest()

    def clear_cache(self):
        if self.__debug:
            print("Cleaning cache!")
        if os.path.exists(self.__cache_dir):
            for root, dirs, files in os.walk(self.__cache_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

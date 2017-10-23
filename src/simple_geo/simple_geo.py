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

import os
import json
import pickle
import hashlib
import pandas as pd
from geopandas import GeoDataFrame
from wfs import wfs
from wtss import wtss

try:
    # For Python 3.0 and later
    from urllib.request import quote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import quote

cache = None


class simple_geo:
    """This class implements a facade for the BDQ WFS and WTSS APIs .


    Attributes:

        wfs (str): the BDQ WFS server URL.
        wtss (str): the BDQ WTSS server URL.
        debug (boolean, optional): enable debug messages
        
    """

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

        self.debug = False
        if 'debug' in kwargs:
            if not type(kwargs['debug']) is bool:
                raise AttributeError('debug must be a boolean')
            self.debug = kwargs['debug']

        self.cache = False
        if 'cache' in kwargs:
            if not type(kwargs['cache']) is bool:
                raise AttributeError('cache must be a boolean')
            self.cache = kwargs['cache']

        self.cache_dir = "./.sgeo/cache"
        if 'cache_dir' in kwargs:
            if not type(kwargs['cache_dir']) is str:
                raise AttributeError('cache_dir must be a str')
            self.cache_dir = kwargs['cache_dir']

        self.wfs = None
        if type(kwargs['wfs'] is str):
            self.wfs_server = kwargs['wfs']
            self.wfs = wfs(kwargs['wfs'], debug=self.debug)
        else:
            raise AttributeError('wfs must be a string')

        self.wtss = None
        if type(kwargs['wtss'] is str):
            self.wtss_server = kwargs['wtss']
            self.wtss = wtss(kwargs['wtss'])
        else:
            raise AttributeError('wtss must be a string')

    def list_features(self):
        """Call wfs list_features"""
        if self.wfs is None:
            raise AttributeError('wfs server is not defined')
        return self.wfs.list_features()

    def describe_feature(self, ft_name):
        """Call wfs describe_feature"""
        if self.wfs is None:
            raise AttributeError('wfs server is not defined')
        return self.wfs.describe_feature(ft_name)

    def feature_collection(self, ft_name, **kwargs):
        """Call wfs feature_collection and format the result to a pandas DataFrame"""
        if self.wfs is None:
            raise AttributeError('wfs server is not defined')
        cv_list = None
        if 'ts' in kwargs:
            cv_list = kwargs['ts']
            del kwargs['ts']
            # TODO: implementar
            raise NotImplementedError('WFS and WTSS integration is not yet implemented')

        fc = None
        if self.cache:
            fc = self._get_cache(self.wfs_server, "feature_collection", ft_name, kwargs)
        if fc is None:
            fc = self.wfs.feature_collection(ft_name, **kwargs)
            if self.cache:
                self._set_cache(self.wfs_server, "feature_collection", ft_name, kwargs, fc)

        metadata = {'total': fc['total'], 'total_features': fc['total_features']}
        if len(fc['features']) == 0:
            return pd.DataFrame(), metadata
        geo_data = pd.DataFrame(fc['features'])
        geo_data = GeoDataFrame(geo_data, geometry='geometry', crs=fc['crs'])

        # retrieve coverage attributes
        if cv_list is not None:
            # TODO: paralelizar essas chamadas
            for cv in cv_list:
                if type(cv['attributes']) is str:
                    cv['attributes'] = tuple([cv['attributes']])
                # create columns as object to support lists
                for c in cv['attributes']:
                    name = '{}.{}'.format(cv['coverage'], c)
                    geo_data[name] = ''
                    geo_data[name] = geo_data[name].astype(object)
                s_date = None
                if 'start_date' in cv:
                    s_date = cv['start_date']
                e_date = None
                if 'end_date' in cv:
                    e_date = cv['end_date']
                for idx, row in geo_data.iterrows():
                    ts, ts_metadata = self.time_series(cv['coverage'],
                                                       cv['attributes'],
                                                       row['geometry'].y,
                                                       row['geometry'].x,
                                                       s_date,
                                                       e_date)
                    for c in cv['attributes']:
                        name = '{}.{}'.format(cv['coverage'], c)
                        if s_date == e_date and s_date is not None:
                            if ts_metadata['total'] == 1:
                                geo_data.set_value(idx, name, ts[c].values.tolist()[0])
                            else:
                                geo_data.set_value(idx, name, None)
                        else:
                            geo_data.set_value(idx, name, ts[c].values.tolist())

        return geo_data, metadata

    def feature_collection_len(self, ft_name, **kwargs):
        """Call bdq wfs feature_collection_len"""
        if self.wfs is None:
            raise AttributeError('wfs server is not defined')

        fc_len = None
        if self.cache:
            fc_len = self._get_cache(self.wfs_server, "feature_collection_len", ft_name, kwargs)
        if fc_len is None:
            fc_len = self.wfs.feature_collection(ft_name, **kwargs)
            if self.cache:
                self._set_cache(self.wfs_server, "feature_collection_len", ft_name, kwargs, fc_len)

        return fc_len

    def list_coverages(self):
        """ Call bdq wtss list_coverages"""
        if self.wtss is None:
            raise AttributeError('wtss server is not defined')
        return self.wtss.list_coverages()

    def describe_coverage(self, cv_name):
        """ Call bdq wtss describe_coverage"""
        if self.wtss is None:
            raise AttributeError('wtss server is not defined')
        return self.wtss.describe_coverage(cv_name)

    def time_series(self, coverage, attributes, latitude, longitude, start_date=None, end_date=None):
        """ Call wtss time_series and format the result to a pandas DataFrame"""
        if self.wtss is None:
            raise AttributeError('wtss server is not defined')

        cv = None
        if self.cache:
            kwargs = {'attributes': attributes, 'latitude': latitude, 'longitude': longitude, 'start_date': start_date,
                      'end_date': end_date}
            cv = self._get_cache(self.wfs_server, "time_series", coverage, kwargs)
        if cv is None:
            cv = self.wtss.time_series(coverage, attributes, latitude, longitude, start_date, end_date)
            if self.cache:
                self._set_cache(self.wfs_server, "time_series", coverage, kwargs, cv)

        data = pd.DataFrame(cv.attributes, index=cv.timeline)
        metadata = {'total': len(cv.timeline)}

        return data, metadata

    def _get_cache(self, server, resource_type, resource_name, kwargs):
        """ Try to get cached request"""
        hash_params = simple_geo._get_cache_hash(server, resource_type, resource_name, kwargs)
        file_path = "{}/{}/{}.pkl".format(self.cache_dir, resource_type, hash_params)
        if os.path.isfile(file_path):
            if os.path.getsize(file_path) > 0:
                with open(file_path, 'rb') as handle:
                    if self.debug:
                        print("Cache found !")
                    content = pickle.load(handle)
                    return content
        if self.debug:
            print("Cache not found !")
        return None

    def _set_cache(self, server, resource_type, resource_name, kwargs, content):
        """ Store a response on cache"""
        hash_params = simple_geo._get_cache_hash(server, resource_type, resource_name, kwargs)
        path_cache = "{}/{}".format(self.cache_dir, resource_type)
        if not os.path.exists(path_cache):
            os.makedirs(path_cache)
        file_path = "{}/{}.pkl".format(path_cache, hash_params)
        with open(file_path, 'wb') as handle:
            pickle.dump(content, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def _get_cache_hash(server, resource_type, resource_name, kwargs):
        """Creates an hash from request parameters"""
        params = "{}.{}.{}.{}".format(server, resource_type, resource_name, json.dumps(kwargs))
        return hashlib.sha256(params).hexdigest()

    def clear_cache(self):
        if self.debug:
            print("Cleaning cache!")
        if os.path.exists(self.cache_dir):
            for root, dirs, files in os.walk(self.cache_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

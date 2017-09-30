#
#   Copyright (C) 2017 National Institute For Space Research (INPE) - Brazil.
#
#  This file is part of Python Client API for BDQ Web Feature Service.
#
#  API for BDQ Web Feature Service is free software: you can
#  redistribute it and/or modify it under the terms of the
#  GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License,
#  or (at your option) any later version.
#
#  API for BDQ Web Feature Service for Python is distributed in the hope that
#  it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with BDQ Web Feature Service for Python. See LICENSE. If not, write to
#  e-sensing team at <esensing-team@dpi.inpe.br>.
#

import json
from xml.dom import minidom
import requests
from wfs import wfs
from wtss import wtss
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point

try:
    # For Python 3.0 and later
    from urllib.request import quote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import quote

cache = None


class bdq:
    """This class implements a facade for the BDQ WFS and WTSS APIs .


    Attributes:

        wfs (str): the BDQ WFS server URL.
        wtss (str): the BDQ WTSS server URL.
        debug (boolean, optional): enable debug messages
        
    """

    def __init__(self, **kwargs):
        """Create a BDQ WFS and BDQ WTSS clients attached to given host addresses.


        Args:
            wfs (str): the BDQ WFS server URL.
            wtss (str): the BDQ WTSS server URL.
            debug (boolean, optional): enable debug messages
        """

        invalid_parameters = set(kwargs) - set(["debug", "wfs", "wtss"]);
        if invalid_parameters:
            raise AttributeError('invalid parameter(s): {}'.format(invalid_parameters))

        self.debug = False
        if 'debug' in kwargs:
            if not type(kwargs['debug']) is bool:
                raise AttributeError('debug must be a boolean')
            self.debug = kwargs['debug']

        if ('wfs' in kwargs) and ('wtss' in kwargs):
            if type(kwargs['wfs'] is str):
                self.wfs_server = kwargs['wfs']
            else:
                raise AttributeError('wfs must be a string')
            if type(kwargs['wtss'] is str):
                self.wtss_server = kwargs['wtss']
            else:
                raise AttributeError('wtss must be a string')
        else:
            raise AttributeError('wfs and wtss must be set')

        self.wfs = wfs(self.wfs_server, debug=self.debug)
        self.wtss = wtss(self.wtss_server)

    def list_features(self):
        """ Call bdq wfs list_features
        """
        return self.wfs.list_features()

    def describe_feature(self, ft_name):
        """ Call bdq wfs describe_feature
        """
        return self.wfs.describe_feature(ft_name)

    def feature_collection(self, ft_name, **kwargs):
        """ Call bdq wfs feature_collection and format the result to a pandas DataFrame
        """
        global cache
        cv_list = None
        if 'ts' in kwargs:
            cv_list = kwargs['ts']
            del kwargs['ts']
        fc = self.wfs.feature_collection(ft_name, **kwargs)
        geo_data = pd.DataFrame(fc['features'])
        geo_data = GeoDataFrame(geo_data, geometry='geometry', crs=fc['crs']['properties']['name'])
        metadata = {'total': fc['total'], 'total_features': fc['total_features']}

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
                    s_date = cv['start_date'];
                e_date = None
                if 'end_date' in cv:
                    e_date = cv['end_date'];
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
        """ Call bdq wfs feature_collection_len
        """
        return self.wfs.feature_collection_len(ft_name, **kwargs)

    def list_coverages(self):
        """ Call bdq wtss list_coverages
        """
        return self.wtss.list_coverages()

    def describe_coverage(self, cv_name):
        """ Call bdq wtss describe_coverage
        """
        return self.wtss.describe_coverage(cv_name)

    def time_series(self, coverage, attributes, latitude, longitude, start_date=None, end_date=None):
        """ Call bdq wtss time_series and format the result to a pandas DataFrame
        """
        cv = self.wtss.time_series(coverage, attributes, latitude, longitude, start_date, end_date)
        data = pd.DataFrame(cv.attributes, index=cv.timeline)
        metadata = {'total': len(cv.timeline)}

        return data, metadata

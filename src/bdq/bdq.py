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

try:
    # For Python 3.0 and later
    from urllib.request import quote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import quote


class bdq:
    """This class implements a facade for the BDQ WFS and WTSS APIs .


    Attributes:

        wfs_server (str): the BDQ WFS server URL.
        wtss_server (str): the BDQ WTSS server URL.
        debug (boolean, optional): enable debug messages
        
    """

    def __init__(self, **kwargs):
        """Create a BDQ WFS and BDQ WTSS clients attached to given host addresses.


        Args:
            wfs_server (str): the BDQ WFS server URL.
            wtss_server (str): the BDQ WTSS server URL.
            debug (boolean, optional): enable debug messages
        """

        invalid_parameters = set(kwargs) - set(["debug", "wfs_server", "wtss_server"]);
        if invalid_parameters:
            raise AttributeError('invalid parameter(s): {}'.format(invalid_parameters))

        self.debug = False
        if 'debug' in kwargs:
            if not type(kwargs['debug']) is bool:
                raise AttributeError('debug must be a boolean')
            self.debug = kwargs['debug']

        if ('wfs_server' in kwargs) and ('wtss_server' in kwargs):
            if type(kwargs['wfs_server'] is str):
                self.wfs_server = kwargs['wfs_server']
            else:
                raise AttributeError('wfs_server must be a string')
            if type(kwargs['wtss_server'] is str):
                self.wtss_server = kwargs['wtss_server']
            else:
                raise AttributeError('wtss_server must be a string')
        else:
            raise AttributeError('wfs_server and wtss_server must be set')

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
        fc = self.wfs.feature_collection(ft_name, **kwargs)
        data = pd.DataFrame(fc['features'])
        metadata = {'total': fc['total'], 'total_features': fc['total_features']}

        return data, metadata

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

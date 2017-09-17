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

try:
    # For Python 3.0 and later
    from urllib.request import quote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import quote


class wfs:
    """This class implements the BDQ WFS API for Python.


    Attributes:

        host (str): the BDQ WFS server URL.

    """

    def __init__(self, host, **kwargs):
        """Create a BDQ WFS client attached to the given host address (an URL).

        Args:
            host (str): the server URL.
            debug (bool): enable debug mode
        """
        self.host = host
        self.base_path = "wfs?service=wfs&version=1.0.0&outputFormat=application/json"
        self.debug = False

        invalid_parameters = set(kwargs) - set(["debug"]);
        if invalid_parameters:
            raise AttributeError('invalid parameter(s): {}'.format(invalid_parameters))
        if 'debug' in kwargs:
            if not type(kwargs['debug']) is bool:
                raise AttributeError('debug must be a boolean')
            self.debug = kwargs['debug']

    def _request(self, uri):
        if self.debug:
            print(uri)
        r = requests.get(uri)
        return r.content

    def list_features(self):
        """Returns the list of all available features in service.

        Returns:
            dict: with a single key/value pair.

            The key named 'features' is associated to a list of str:
            { 'features' : ['ft1', 'ft2', ..., 'ftn'] }

        Raises:
            ValueError: if feature name parameter is missing.
            Exception: if the service returns a expcetion
        """
        doc = self._request("{}/{}&request=GetCapabilities".format(self.host, self.base_path))
        if 'exception' in doc:
            raise Exception(doc["exception"])

        xmldoc = minidom.parseString(doc)
        itemlist = xmldoc.getElementsByTagName('FeatureType')

        features = dict()
        features[u'features'] = []

        for s in itemlist:
            features[u'features'].append(s.childNodes[0].firstChild.nodeValue)

        return features

    def describe_feature(self, ft_name):
        """Returns the metadata of a given feature.

        Args:
            ft_name (str): the feature name whose schema you are interested in.

        Returns:
            dict: a dictionary with some metadata about the informed feature.

        Raises:
            ValueError: if feature parameter is missing.
            AttributeError: if found an unexpected parameter type
            Exception: if the service returns a expcetion
        """

        if not ft_name:
            raise ValueError("Missing feature name.")

        doc = self._request("{}/{}&request=DescribeFeatureType&typeName={}".format(self.host, self.base_path, ft_name))
        if 'exception' in doc:
            raise Exception(doc["exception"])

        js = json.loads(doc)

        feature = dict()
        feature['name'] = js['featureTypes'][0]['typeName']
        feature['namespace'] = js['targetPrefix']
        feature['full_name'] = "{}:{}".format(feature['namespace'], feature['name'])

        feature['attributes'] = []
        for prop in js['featureTypes'][0]['properties']:
            feature['attributes'].append({'name': prop['name'], 'datatype': prop['localType']})

        return feature

    def feature_collection(self, ft_name, **kwargs):
        """Retrieve the feature collection given feature.

        Args:

            ft_name (str): the feature name whose you are interested in.
            max_features (int, optional): the number of records to get
            attributes(list, tuple, str, optional): the list, tuple or string of attributes you are interested in to have the feature collection.
            within(str, optional): a Polygon/MultiPolygon in Well-known text (WKT) format used filter features
            filter(list, tuple, str, optional): the list, tuple or string of cql filter (http://docs.geoserver.org/latest/en/user/filter/function_reference.html#filter-function-reference)
            sort_by(list, tuple, str, optional(: the list, tuple or string of attributes used to sort resulting collection

        Raises:
            ValueError: if latitude or longitude is out of range or any mandatory parameter is missing.
            AttributeError: if found an unexpected parameter or unexpected type
            Exception: if the service returns a expcetion
        """
        if not ft_name:
            raise ValueError("Missing feature name.")

        invalid_parameters = set(kwargs) - set(["max_features", "attributes", "within", "filter", "sort_by"]);
        if invalid_parameters:
            raise AttributeError('invalid parameter(s): {}'.format(invalid_parameters))

        max_features = ""
        if 'max_features' in kwargs:
            max_features = "&maxFeatures={}".format(kwargs['max_features'])

        attributes = ""
        if 'attributes' in kwargs:
            if type(kwargs['attributes']) in [list, tuple]:
                kwargs['attributes'] = ",".join(kwargs['attributes'])
            elif not type(kwargs['attributes']) is str:
                raise AttributeError('attributes must be a list, tuple or string')
            attributes = "&propertyName=geometria,{}".format(kwargs['attributes'])

        sort_by = ""
        if 'sort_by' in kwargs:
            if type(kwargs['sort_by']) in [list, tuple]:
                kwargs['sort_by'] = ",".join(kwargs['sort_by'])
            elif not type(kwargs['sort_by']) is str:
                raise AttributeError('sort_by must be a list, tuple or string')
            sort_by = "&sortBy={}".format(kwargs['sort_by'])

        cql_filter = ""
        if 'within' in kwargs:
            if not type(kwargs['within']) is str:
                raise AttributeError('within must be a string')
            cql_filter = "&CQL_FILTER=WITHIN(geometria,{})".format(quote(kwargs['within']))

        if 'filter' in kwargs:
            if type(kwargs['filter']) in [list, tuple]:
                kwargs['filter'] = "+AND+".join(kwargs['filter'])
            elif not type(kwargs['filter']) is str:
                raise AttributeError('filter must be a list, tuple or string')
            if not cql_filter:
                cql_filter = "&CQL_FILTER="
            else:
                cql_filter += "+AND+"
            cql_filter += kwargs['filter']

        doc = self._request(
            "{}/{}&request=GetFeature&typeName={}{}{}{}{}".format(self.host, self.base_path, ft_name, max_features,
                                                                  attributes, cql_filter, sort_by))
        if 'exception' in doc:
            raise Exception(doc["exception"])

        js = json.loads(doc)

        fc = dict()
        fc['total_features'] = js['totalFeatures']
        fc['total'] = len(js['features'])
        fc['features'] = [];
        for item in js['features']:
            feature = {'coordinates': item['geometry']['coordinates']};
            feature.update(item['properties'])
            fc['features'].append(feature)

        return fc

    def feature_collection_len(self, ft_name, **kwargs):
        """Retrieve the feature collection length .

                Args:

                    ft_name (str): the feature name whose you are interested in.
                    within(str, optional): a Polygon/MultiPolygon in Well-known text (WKT) format used filter features
                    filter(list, tuple, str, optional): the list, tuple or string of cql filter (http://docs.geoserver.org/latest/en/user/filter/function_reference.html#filter-function-reference)

                Raises:
                    ValueError: if latitude or longitude is out of range or any mandatory parameter is missing.
                    AttributeError: if found an unexpected parameter or unexpected type
                    Exception: if the service returns a expcetion
                """
        if not ft_name:
            raise ValueError("Missing feature name.")

        invalid_parameters = set(kwargs) - set(["within", "filter"]);
        if invalid_parameters:
            raise AttributeError('invalid parameter(s): {}'.format(invalid_parameters))

        max_features = "&maxFeatures=1"
        attributes = "&propertyName=id"
        sort_by = ""

        cql_filter = ""
        if 'within' in kwargs:
            if not type(kwargs['within']) is str:
                raise AttributeError('within must be a string')
            cql_filter = "&CQL_FILTER=WITHIN(geometria,{})".format(quote(kwargs['within']))

        if 'filter' in kwargs:
            if type(kwargs['filter']) in [list, tuple]:
                kwargs['filter'] = "+AND+".join(kwargs['filter'])
            elif not type(kwargs['filter']) is str:
                raise AttributeError('filter must be a list, tuple or string')
            if not cql_filter:
                cql_filter = "&CQL_FILTER="
            else:
                cql_filter += "+AND+"
            cql_filter += kwargs['filter']

        doc = self._request(
            "{}/{}&request=GetFeature&typeName={}{}{}{}{}".format(self.host, self.base_path, ft_name, max_features,
                                                                  attributes, cql_filter, sort_by))
        if 'exception' in doc:
            raise Exception(doc["exception"])

        js = json.loads(doc)

        return js['totalFeatures']

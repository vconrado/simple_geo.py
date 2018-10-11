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

import json
from xml.dom import minidom
import requests
from shapely.geometry import Point, Polygon, MultiPolygon

try:
    # For Python 3.0 and later
    from urllib.request import quote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import quote


class wfs:
    """This class implements the WFS client.
    Attributes:
        host (str): the WFS server URL.
    """

    def __init__(self, host, **kwargs):
        """Create a WFS client attached to the given host address (an URL).
        Args:
            host (str): the server URL.
            debug (bool): enable debug mode
        """
        self.host = host
        self.base_path = "wfs?service=wfs&version=1.0.0&outputFormat=application/json"
        self.debug = False

        invalid_parameters = set(kwargs) - {"debug"}
        if invalid_parameters:
            raise AttributeError('invalid parameter(s): {}'.format(invalid_parameters))
        if 'debug' in kwargs:
            if not type(kwargs['debug']) is bool:
                raise AttributeError('debug must be a boolean')
            self.debug = kwargs['debug']

    def _get(self, uri):
        if self.debug:
            print("GET", uri)
        r = requests.get(uri)
        return r.content

    def _post(self, uri, data=None):
        if self.debug:
            print("POST", uri)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.post(uri, data=data, headers=headers)
        return r.text

    def list_features(self):
        """Returns the list of all available features in service.

        Returns:
            dict: with a single key/value pair

        Raises:
            ValueError: if feature name parameter is missing
            Exception: if the service returns a exception
        """
        doc = self._get("{}/{}&request=GetCapabilities".format(self.host, self.base_path))
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
            Exception: if the service returns a exception
        """

        if not ft_name:
            raise ValueError("Missing feature name.")

        doc = self._get("{}/{}&request=DescribeFeatureType&typeName={}".format(self.host, self.base_path, ft_name))
        if 'exception' in doc:
            raise Exception(doc["exception"])

        js = json.loads(doc)

        feature = dict()
        feature['name'] = js['featureTypes'][0]['typeName']
        feature['namespace'] = js['targetPrefix']
        feature['full_name'] = "{}:{}".format(feature['namespace'], feature['name'])

        feature['attributes'] = []
        for prop in js['featureTypes'][0]['properties']:
            attr = {'name': prop['name'], 'localtype': prop['localType'], 'type': prop['type']}
            feature['attributes'].append(attr)
            if prop['type'] in ['gml:MultiPolygon', 'gml:Point']:
                feature['geometry'] = attr

        return feature

    def feature_collection(self, ft_name, **kwargs):
        """Retrieve the feature collection given feature.

        Args:
            ft_name (str): the feature name whose you are interested in.
             **kwargs: Keyword arguments:
                max_features (int, optional): the number of records to get
                attributes(list, tuple, str, optional): the list, tuple or string of attributes you are interested in
                            to have the feature collection.
                within(str, optional): a Polygon/MultiPolygon in Well-known text (WKT) format used filter features
                filter(list, tuple, str, optional): the list, tuple or string of cql filter
                    (http://docs.geoserver.org/latest/en/user/filter/function_reference.html#filter-function-reference)
                sort_by(list, tuple, str, optional(: the list, tuple or string of attributes used to sort resulting
                    collection

        Raises:
            ValueError: if latitude or longitude is out of range or any mandatory parameter is missing.
            AttributeError: if found an unexpected parameter or unexpected type
            Exception: if the service returns a exception
        """
        if not ft_name:
            raise ValueError("Missing feature name.")

        invalid_parameters = set(kwargs) - {"max_features", "attributes", "filter", "sort_by"}

        if invalid_parameters:
            raise AttributeError('invalid parameter(s): {}'.format(invalid_parameters))

        feature_desc = self.describe_feature(ft_name)
        geometry_name = feature_desc['geometry']['name']

        data = {
            'typeName': ft_name
        }

        if 'max_features' in kwargs:
            data['maxFeatures'] = kwargs['max_features']

        if 'attributes' in kwargs:
            if type(kwargs['attributes']) in [list, tuple]:
                kwargs['attributes'] = ",".join(kwargs['attributes'])
            elif not type(kwargs['attributes']) is str:
                raise AttributeError('attributes must be a list, tuple or string')
            if len(kwargs['attributes']) > 0:
                data['propertyName'] = "{},{}".format(geometry_name, kwargs['attributes'])

        if 'sort_by' in kwargs:
            if type(kwargs['sort_by']) in [list, tuple]:
                kwargs['sort_by'] = ",".join(kwargs['sort_by'])
            elif not type(kwargs['sort_by']) is str:
                raise AttributeError('sort_by must be a list, tuple or string')
            data['sortBy'] = kwargs['sort_by']

        if 'filter' in kwargs:
            if type(kwargs['filter']) is not str:
                raise AttributeError('filter must be a string')
            data['CQL_FILTER'] = kwargs['filter'].replace("#geom#", geometry_name)

        body = ""
        for key, value in data.iteritems():
            if value:
                body += "&{}={}".format(key, value)
        doc = self._post("{}/{}&request=GetFeature".format(self.host, self.base_path), data=body[1:])

        if 'exception' in doc:
            raise Exception(doc["exception"])

        js = json.loads(doc)

        fc = dict()
        fc['total_features'] = js['totalFeatures']
        fc['total'] = len(js['features'])
        fc['features'] = []
        for item in js['features']:
            if feature_desc['geometry']['type'] == 'gml:Point':
                feature = {'geometry': Point(item['geometry']['coordinates'][0], item['geometry']['coordinates'][1])}
            elif feature_desc['geometry']['type'] == 'gml:MultiPolygon':
                polygons = []
                for polygon in item['geometry']['coordinates']:
                    polygons += [Polygon(lr) for lr in polygon]
                feature = {'geometry': MultiPolygon(polygons)}
            else:
                raise Exception('Unsupported geometry type.')
            feature.update(item['properties'])
            fc['features'].append(feature)
        fc['crs'] = js['crs']
        return fc

    def feature_collection_len(self, ft_name, **kwargs):
        """Retrieve the feature collection length
            Args:
            ft_name (str): the feature name whose you are interested in.
            **kwargs: Keyword arguments:
                within(str, optional): a Polygon/MultiPolygon in Well-known text (WKT) format used
                    filter features
                filter(list, tuple, str, optional): the list, tuple or string of cql filter
                    (http://docs.geoserver.org/latest/en/user/filter/function_reference.html#filter-function-reference)
            Raises:
                ValueError: if latitude or longitude is out of range or any mandatory parameter is missing.
                AttributeError: if found an unexpected parameter or unexpected type
                Exception: if the service returns a exception
        """
        if not ft_name:
            raise ValueError("Missing feature name.")

        invalid_parameters = set(kwargs) - {"within", "filter"}
        if invalid_parameters:
            raise AttributeError('invalid parameter(s): {}'.format(invalid_parameters))

        kwargs['max_features'] = 1
        fc = self.feature_collection(ft_name, **kwargs)

        return fc['total_features']

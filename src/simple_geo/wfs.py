# -*- coding: utf-8 -*-
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
import requests
from shapely.geometry import Point, Polygon, MultiPolygon
from osgeo import ogr

try:
    # For Python 3.0 and later
    from urllib.request import quote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import quote

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


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
        self.base_path = "wfs?service=wfs&version=1.1.0&outputFormat=application/json"
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

    def _post(self, uri, data):
        if self.debug:
            print(uri)
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(uri, data=data, headers=headers)
        return r.text

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
            attr = {'name': prop['name'], 'localtype': prop['localType'], 'type': prop['type']}
            feature['attributes'].append(attr)
            if prop['type'] in ['gml:MultiPolygon', 'gml:Point']:
                feature['geometry'] = attr

        return feature

    def feature_collection(self, ft_name, **kwargs):
        """Retrieve the feature collection given feature.
        Args:
            ft_name (str): the feature name whose you are interested in.
            max_features (int, optional): the number of records to get
            attributes(list, tuple, str, optional): the list, tuple or string of attributes you are interested in to have the feature collection.
            spatial_filter(str, optional): a Polygon/MultiPolygon in Well-known text (WKT) format used filter features
            filter(list, tuple, str, optional): the list, tuple or string of cql filter (http://docs.geoserver.org/latest/en/user/filter/function_reference.html#filter-function-reference)
            sort_by(list, tuple, str, optional): the list, tuple or string of attributes used to sort resulting collection
            srs(str, optional): set srs for spatial filter operations. Default: EPSG:4326
        Raises:
            ValueError: if latitude or longitude is out of range or any mandatory parameter is missing.
            AttributeError: if found an unexpected parameter or unexpected type
            Exception: if the service returns a expcetion
        """

        if not ft_name:
            raise ValueError("Missing feature name.")

        invalid_parameters = set(kwargs) - set(
            ['max_features', 'attributes', 'filter', 'sort_by', 'spatial_filter', 'srs']);
        if invalid_parameters:
            raise AttributeError('invalid parameter(s): {}'.format(invalid_parameters))

        desc = self.describe_feature(ft_name)
        geometry_name = desc['geometry']['name']

        root_node = wfs._create_get_feature_xml(ft_name)

        if 'srs' in kwargs:
            if type(kwargs['srs']) is not str:
                raise AttributeError('srs must be a string')
            srs = kwargs['kwargs']
        else:
            srs = 'EPSG:4326'

        if 'max_features' in kwargs:
            wfs._handle_max_features(root_node, kwargs['max_features'])

        query_node = root_node.findall('{http://www.opengis.net/wfs}Query')[0]

        if 'attributes' in kwargs:
            wfs._handle_attributes(query_node, kwargs['attributes'], geometry_name)

        if 'sort_by' in kwargs:
            wfs._handle_sort_by(query_node, kwargs['sort_by'])

        if 'filter' in kwargs or 'spatial_filter' in kwargs:

            filter_dom = ET.SubElement(query_node, "{http://www.opengis.net/ogc}Filter")
            and_dom = ET.SubElement(filter_dom, "And")

            if 'filter' in kwargs:
                wfs._handle_filter(and_dom, kwargs['filter'])

            if 'spatial_filter' in kwargs:
                wfs._handle_spatial_filter(and_dom, kwargs['spatial_filter'], geometry_name, srs)

        doc = self._post("{}/{}".format(self.host, self.base_path), ET.tostring(root_node, 'utf-8'))
        if len(doc) < 1:
            raise Exception('Server returns an empty message')

        if 'exception' in doc:
            raise Exception(doc["exception"])

        js = json.loads(doc)

        fc = dict()
        fc['total_features'] = js['totalFeatures']
        fc['total'] = len(js['features'])
        fc['features'] = [];
        for item in js['features']:
            if desc['geometry']['type'] == 'gml:Point':
                feature = {'geometry': Point(item['geometry']['coordinates'][0], item['geometry']['coordinates'][1])};
            elif desc['geometry']['type'] == 'gml:MultiPolygon':
                polygons = []
                for polygon in item['geometry']['coordinates']:
                    polygons += [Polygon(lr) for lr in polygon]

                feature = {'geometry': MultiPolygon(polygons)};
            else:
                raise Exception('Unsupported geometry type.')
            feature.update(item['properties'])
            fc['features'].append(feature)
        fc['crs'] = js['crs']
        return fc

    @staticmethod
    def _create_get_feature_xml(feature_name):

        ET.register_namespace('wfs', "http://www.opengis.net/wfs")
        ET.register_namespace('ogc', "http://www.opengis.net/ogc")
        ET.register_namespace('gml', "http://www.opengis.net/gml")

        xml_get_feature_template = """<wfs:GetFeature service='WFS' version='1.1.0'
                outputFormat='JSON' 
                  xmlns:wfs='http://www.opengis.net/wfs' 
                  xmlns:ogc='http://www.opengis.net/ogc' 
                  xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' 
                  xsi:schemaLocation='http://www.opengis.net/wfs 
                                      http://schemas.opengis.net/wfs/1.0.0/WFS-basic.xsd'> 
                  <wfs:Query typeName='{}'> 
                </wfs:Query>
                </wfs:GetFeature>""".format(feature_name)

        return ET.fromstring(xml_get_feature_template)

    @staticmethod
    def _handle_max_features(node, max_features_param):
        if max_features_param < 1:
            raise AttributeError('max_features must must be positive and nonzero.')
        node.set('maxFeatures', str(max_features_param))

    @staticmethod
    def _handle_attributes(node, attributes_param, geometry_name):
        if type(attributes_param) not in [tuple, list, str]:
            raise AttributeError('attributes must be a list, tuple or string')

        if type(attributes_param) is str:
            attributes_param = [attributes_param, ]

        if type(attributes_param) in [list, tuple]:
            attributes = set(attributes_param)
            attributes.add(geometry_name)

            for attr in attributes:
                pn_node = ET.SubElement(node, "{http://www.opengis.net/ogc}PropertyName")
                pn_node.text = attr

    @staticmethod
    def _handle_filter(node, filter_param):
        if type(filter_param) is not dict:
            raise AttributeError('filter must be a dict')

        for name, value in filter_param.iteritems():
            prop_equal_node = ET.SubElement(node, "PropertyIsEqualTo")

            pn_node = ET.SubElement(prop_equal_node, "PropertyName")
            pn_node.text = name

            literal_node = ET.SubElement(prop_equal_node, "Literal")
            literal_node.text = value

    @staticmethod
    def _handle_sort_by(node, sort_by_param):
        if type(sort_by_param) not in [tuple, list, str, dict]:
            raise AttributeError('sort_by must be a dict, list, tuple or string')

        if type(sort_by_param) is str:
            sort_by_param = [sort_by_param, ]

        if type(sort_by_param) is not dict:
            sort_by = {}
            for attr in sort_by_param:
                sort_by[attr] = 'ASC'
        else:
            sort_by = sort_by_param

        sort_by_node = ET.SubElement(node, "{http://www.opengis.net/ogc}SortBy")
        for attr, order in sort_by.iteritems():
            if order not in ['ASC', 'DESC']:
                raise AttributeError("Invalid order {}.".format(order))
            sort_prop_node = ET.SubElement(sort_by_node, "{http://www.opengis.net/ogc}SortProperty")
            pn_node = ET.SubElement(sort_prop_node, "{http://www.opengis.net/ogc}PropertyName")
            pn_node.text = attr
            sort_order_node = ET.SubElement(sort_prop_node, "{http://www.opengis.net/ogc}SortOrder")
            sort_order_node.text = order

    @staticmethod
    def _handle_spatial_filter(node, spatial_filter_param, geometry_name, srs):

        # http://www.datypic.com/sc/niem20/s-filter.xsd.html
        spatial_op_dict = {
            'within': 'Within',
            'intersects': 'Intersects',
            'overlaps': 'Overlaps',
            'touches': 'Touches',
            'contain': 'Contains',
            'crosses': 'Crosses',
            'disjoint': 'Disjoint'
        }
        if type(spatial_filter_param) is not dict:
            raise AttributeError('spatial_filter must be a dict')

        for spatial_op, wkt in spatial_filter_param.iteritems():
            geom = ogr.CreateGeometryFromWkt(wkt)
            # //wfs._handle_spatial_filter(and_dom, spatial_op, geom, geometry_name)

            if spatial_op not in spatial_op_dict:
                raise AttributeError(
                    'Invalid spatial_filter operation. Supported operations: {}'.format(spatial_op_dict.keys()))

            op_node = ET.SubElement(node, "{http://www.opengis.net/ogc}" + spatial_op_dict[spatial_op])
            pn = ET.SubElement(op_node, "{http://www.opengis.net/ogc}PropertyName")
            pn.text = geometry_name

            gml3 = geom.ExportToGML(["FORMAT=GML32"])
            # add namespace to root element
            if geom.GetGeometryName() == "MULTIPOLYGON":
                gml3 = gml3.replace("MultiSurface>",
                                    "MultiSurface xmlns:gml=\"http://www.opengis.net/gml\">",
                                    1)
            else:
                raise Exception('Unsupported geometry type for spatial_filter.')

            geometry_node = ET.fromstring(gml3);
            geometry_node.set('xmlns:gml', "http://www.opengis.net/gml")
            geometry_node.set('srsName', srs)

            op_node.append(geometry_node)

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

        invalid_parameters = set(kwargs) - set(['filter', 'spatial_filter', 'srs']);
        if invalid_parameters:
            raise AttributeError('invalid parameter(s): {}'.format(invalid_parameters))

        kwargs['max_features'] = 1
        fc = self.feature_collection(ft_name, **kwargs)

        return fc['total_features']

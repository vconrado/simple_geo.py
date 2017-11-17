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
import shapely


class Predicates:

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
        return "{}<>'{}'".format(op1, op2)

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
        return "WITHIN(#geom#, {})".format(convert_shapely_to_wkt(wkt))

    @staticmethod
    def INTERSECTS(wkt):
        return "INTERSECTS(#geom#, {})".format(convert_shapely_to_wkt(wkt))


def convert_shapely_to_wkt(obj):
    if type(obj) is str:
        return obj
    elif type(obj) in (shapely.geometry.point.Point, shapely.geometry.multipolygon.MultiPolygon):
        return obj.wkt
    else:
        raise AttributeError('This attribute must be an array, Point or MultiPolygon', obj)

        # spatial_op_dict = {
        #             'within': 'Within',
        #             'intersects': 'Intersects',
        #             'overlaps': 'Overlaps',
        #             'touches': 'Touches',
        #             'contain': 'Contains',
        #             'crosses': 'Crosses',
        #             'disjoint': 'Disjoint'
        #         }

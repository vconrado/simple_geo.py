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


class TimeSerie:
    def __init__(self, simple_geo, coverage, **kwargs):
        """Create TimeSerie object.
        Args:
            name(str): TimeSerie Name
            **kwargs: Keyword arguments:
                debug (boolean, optional): enable debug messages
        """
        # if type(simple_geo) is not SimpleGeo:
        #     raise AttributeError('simple_geo must be a SimpleGeo object')

        self.__simple_geo = simple_geo
        self._coverage = coverage
        self._start_date = None
        self._end_date = None

    def period(self, start_date, end_date):
        if type(start_date) is str and type(end_date) is str:
            self._start_date = start_date
            self._end_date = end_date
        else:
            raise AttributeError('period dates must be string (YYYY-MM-DD)')
        return self

    def date(self, start_date):
        return self.period(start_date, start_date)

    def get(self, pos):
        if type(pos) in (list, tuple):
            tss = []
            for p in pos:
                tss.append(self.__simple_geo.get(self, pos=p))
            return tss
        return self.__simple_geo.get(self, pos=pos)

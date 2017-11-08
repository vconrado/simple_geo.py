# -*- coding: utf-8 -*-
import sys
import os

from shapely.geometry.point import Point as Point

# to use local version of simple_geo
sys.path.insert(0, '../src/SimpleGeo')

from SimpleGeo import SimpleGeo, Operations as op

s = SimpleGeo(wfs="http://wfs_server:8080/geoserver-esensing", wtss="http://wtss_server:7654", debug=False, cache=False)

print(s.features())
f = s.feature("esensing:focos_bra_2016") \
    .attributes(["id", "municipio", "timestamp", "regiao"]) \
    .filter(op.OR(
    op.AND(
        op.EQ("satelite_referencia", "true"),
        op.GE("timestamp", "2016-01-01"),
        op.LT("timestamp", "2016-02-01"),
        op.WITHIN(
            "POLYGON((-49.515628859948507 -19.394602563415745,-48.020567850467053 -19.610579617637825,-48.354439522883652 -21.052347219666608,-49.849500507163917 -20.836369963642884,-49.515628859948507 -19.394602563415745))"),
    ), \
    op.NE("regiao", "SE") \
    )) \
    .max_features(10) \
    .sort_by("regiao")
# print(f)
print(f.describe())
# dados = f.get()
# print(dados)
# print("total_features", dados.total_features)


sp = s.feature("esensing:estados_bra") \
    .filter(op.EQ("nome", "São Paulo")) \
    .max_features(20)
sp_data = sp.get()
print(sp_data)

f = s.feature("esensing:focos_bra_2016") \
    .attributes(["id", "municipio", "timestamp", "regiao"]) \
    .filter(op.OR(
    op.AND( \
        op.GE("timestamp", "2016-01-01"), \
        op.LT("timestamp", "2016-02-01"), \
        op.WITHIN(sp_data.loc[0, 'geometry'])
    ), \
    op.EQ("timestamp", "2016-12-12") \
    )) \
    .max_features(20) \
    .sort_by(op.ASC("timestamp"))


#print(f)
print(f.describe())
dados = f.get()
print(dados)
# print(dados.loc[0,'geometry'])
# print("total_features", dados.total_features)



#
print(s.coverages())
c = s.coverage("rpth") \
    .attributes(["precipitation", "risk", "temperature", "humidity"])

ts = s.time_serie(c) \
    .period("2016-01-01", "2016-12-31")
ts_data = ts.get(Point(-54.0, -12.0))
print(ts_data)
print(ts_data.total)


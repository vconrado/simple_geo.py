# -*- coding: utf-8 -*-

from context import SimpleGeo, Predicates as pre
from shapely.geometry import Point

s = SimpleGeo(wfs="http://wfs_server:8080/geoserver-esensing", wtss="http://wtss_server:7654", debug=False, cache=False)

print(s.features())
f = s.feature("esensing:focos_bra_2016") \
    .attributes(["id", "municipio", "timestamp", "regiao"]) \
    .filter(pre.OR(
    pre.AND(
        pre.EQ("satelite_referencia", "true"),
        pre.GE("timestamp", "2016-01-01"),
        pre.LT("timestamp", "2016-02-01"),
        pre.WITHIN(
            "POLYGON((-49.515628859948507 -19.394602563415745,-48.020567850467053 -19.610579617637825,-48.354439522883652 -21.052347219666608,-49.849500507163917 -20.836369963642884,-49.515628859948507 -19.394602563415745))"),
    ), \
    pre.NE("regiao", "SE") \
    )) \
    .max_features(10) \
    .sort_by("regiao")
print(f.describe())
# dados = f.get()
# print(dados)
# print("total_features", dados.total_features)


sp = s.feature("esensing:estados_bra") \
    .filter(pre.EQ("nome", "São Paulo")) \
    .max_features(20)
sp_data = sp.get()
print(sp_data)

f = s.feature("esensing:focos_bra_2016") \
    .attributes(["id", "municipio", "timestamp", "regiao"]) \
    .filter(pre.OR(
    pre.AND( \
        pre.GE("timestamp", "2016-01-01"), \
        pre.LT("timestamp", "2016-02-01"), \
        pre.WITHIN(sp_data.loc[0, 'geometry'])
    ), \
    pre.EQ("timestamp", "2016-12-12") \
    )) \
    .max_features(20) \
    .sort_by(pre.ASC("timestamp"))

print(f.describe())
dados = f.get()
print(dados)
print("total_features", dados.total_features)

#
print(s.coverages())
c = s.coverage("rpth") \
    .attributes(["precipitation", "risk", "temperature", "humidity"])

ts = s.time_serie(c) \
    .period("2016-01-01", "2016-01-09")

ts_data = ts.get([Point(-54.0, -12.0), Point(-54.0, -13.0)])
print(len(ts_data))
print(ts_data)

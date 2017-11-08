# -*- coding: utf-8 -*-
import sys
import os

# to use local version of simple_geo
sys.path.insert(0, '../src/SimpleGeo')

from SimpleGeo import SimpleGeo, Operations as op

s = SimpleGeo(wfs="http://wfs_server:8080/geoserver-esensing", wtss="http://wtss_server:7654", debug=False, cache=False)

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

f = s.feature("esensing:focos_bra_2016") \
    .attributes(["id", "municipio", "timestamp", "regiao"]) \
    .filter(op.OR(
    op.AND( \
        # op.EQ("regiao", "NE"), \
        op.GE("timestamp", "2016-01-01"), \
        op.LT("timestamp", "2016-02-01"), \
        op.WITHIN(
            "POLYGON((-49.515628859948507 -19.394602563415745,-48.020567850467053 -19.610579617637825,-48.354439522883652 -21.052347219666608,-49.849500507163917 -20.836369963642884,-49.515628859948507 -19.394602563415745))")
    ), \
    op.EQ("timestamp", "2016-12-12") \
    )) \
    .max_features(20) \
    .sort_by(op.ASC("timestamp"))

print(f)
dados = f.get()
print(dados)
print("total_features", dados.total_features)

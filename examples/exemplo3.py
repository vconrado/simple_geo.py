# -*- coding: utf-8 -*-

from context import SimpleGeo, Predicates as pre
from shapely.geometry import Point

s = SimpleGeo(wfs="http://www.terrama2.dpi.inpe.br/e-sensing/geoserver", wtss="http://www.terrama2.dpi.inpe.br/e-sensing", debug=False, cache=False)

print(s.features())

f = s.feature('esensing:amostras_cerrado')
print(f.get())


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
dados = f.get()
print(dados)
print("total_features", dados.total_features)


# Getting SP state
sp = s.feature("esensing:estados_bra") \
    .filter(pre.EQ("nome", "São Paulo")) \
    .max_features(20)
sp_data = sp.get()
print(sp_data)

# Getting Focos using SP polygon
f = s.feature("esensing:focos_bra_2016") \
    .attributes(["id", "municipio", "timestamp", "regiao"]) \
    .filter(pre.OR(
    pre.AND(
        pre.GE("timestamp", "2016-01-01"),
        pre.LT("timestamp", "2016-02-01"),
        pre.WITHIN(sp_data.loc[0, 'geometry'])
    ),
    pre.EQ("timestamp", "2016-12-12"))) \
    .max_features(20) \
    .sort_by(pre.ASC("timestamp"))

print(f.describe())
focos_data = f.get()
print(focos_data)
print("total_features", focos_data.total_features)

# Time Series
print(s.coverages())
c = s.coverage("rpth") \
    .attributes(["precipitation", "risk", "temperature", "humidity"])

ts = s.time_series(c) \
    .period("2016-01-01", "2016-01-09")

ts_data = ts.get(Point(-54.0, -12.0))
print(ts_data)

ts_data = ts.get([Point(-54.0, -12.0), Point(-54.0, -13.0)])
print(ts_data)

# Integrating Features and TimeSeries
c = s.coverage("rpth") \
    .attributes(["precipitation", "risk", "temperature", "humidity"])
ts = s.time_series(c)

f = s.feature("esensing:focos_bra_2016") \
    .attributes(
    ["id", "municipio", "timestamp", "regiao",
     {'time_series': ts, 'start_date': 0, 'end_date': 0, 'datetime': 'timestamp'}]) \
    .sort_by("timestamp") \
    .max_features(5)


# {'time_serie': ts, 'date': 0, 'datetime': 'timestamp'}]) \
# {'time_serie': ts, 'start_date': 0, 'end_date': 4, 'datetime': 'timestamp'}]) \

ft_ts_data = f.get()
print(ft_ts_data)

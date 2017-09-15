import sys

# to use local version of bdq
sys.path.insert(0, '../src/bdq')

from bdq import bdq

b = bdq("http://my_geoserver:8080/geoserver-esensing/", debug=True)

ft_list = b.list_features()

print(ft_list)

ft_scheme = b.describe_feature("esensing:focos_bra_2016")

print(ft_scheme)

fc = b.feature_collection("esensing:focos_bra_2016",
                          attributes=("id", "municipio", "timestamp", "regiao"),
                          within="POLYGON((-49.515628859948507 -19.394602563415745,-48.020567850467053 -19.610579617637825,-48.354439522883652 -21.052347219666608,-49.849500507163917 -20.836369963642884,-49.515628859948507 -19.394602563415745))",
                          filter=["satelite_referencia='true'", "timestamp>='2016-01-01'", "timestamp<'2016-02-01'"],
                          sort_by="regiao,municipio",
                          max_features=10)
# print(fc)
for f in fc['features']:
    print("{} {} {}".format(f['id'], f['municipio'].encode('utf-8'), f['regiao']))

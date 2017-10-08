import sys

# to use local version of simple_geo
sys.path.insert(0, '../src/simple_geo')

from simple_geo import simple_geo as sgeo

######################################################################################################################
# simple_geo Features

s = sgeo(wfs="http://localhost:8080/geoserver-esensing", wtss="http://localhost:7654/ts", debug=True)

print("Features")
# Retrieving the list of all available features in the service
ft_list = s.list_features()
print(ft_list)

# Retrieving the metadata of a given feature
ft_scheme = s.describe_feature("esensing:focos_bra_2016")
print(ft_scheme)

# Retrieving the collection for a given feature
#fc, fc_metadata = b.feature_collection("esensing:focos_bra_2016")


# Retrieving a selected elements for a given feature
fc, fc_metadata = s.feature_collection("esensing:focos_bra_2016",
                                       attributes=("id", "municipio", "timestamp", "regiao"),
                                       within="POLYGON((-49.515628859948507 -19.394602563415745,-48.020567850467053 -19.610579617637825,-48.354439522883652 -21.052347219666608,-49.849500507163917 -20.836369963642884,-49.515628859948507 -19.394602563415745))",
                                       filter=["satelite_referencia='true'", "timestamp>='2016-01-01'",
                                               "timestamp<'2016-02-01'"],
                                       sort_by=("regiao", "municipio"),
                                       max_features=10)
print(fc)
print(fc_metadata)

# Retrieving collection length of selected elements for a given feature
fc_len = s.feature_collection_len("esensing:focos_bra_2016",
                                  within="POLYGON((-49.515628859948507 -19.394602563415745,-48.020567850467053 -19.610579617637825,-48.354439522883652 -21.052347219666608,-49.849500507163917 -20.836369963642884,-49.515628859948507 -19.394602563415745))",
                                  filter=["satelite_referencia='true'", "timestamp>='2016-01-01'",
                                          "timestamp<'2016-02-01'"])
print(fc_len)

######################################################################################################################
# BDQ Coverages

print("\n\nCoverages")

# Retrieving the list of all available coverages in the service
cv_list = s.list_coverages()
print(cv_list)

# Retrieving the metadata of a given coverage
cv_scheme = s.describe_coverage("climatologia")
print(cv_scheme)

# Retrieving the time series for a given location
ts, ts_metadata = s.time_series("climatologia", ("precipitation", "temperature", "humidity"), -12, -54)
print(ts)
print(ts_metadata)

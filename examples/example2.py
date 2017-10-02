import sys

# to use local version of bdq
sys.path.insert(0, '../src/simple_geo')

from simple_geo import simple_geo as sgeo

######################################################################################################################
# BDQ Features

s = sgeo(wfs="http://localhost:8080/geoserver-esensing/", wtss="http://www.dpi.inpe.br/ts", debug=True)

# Retrieving a selected elements for a given feature
fc, fc_metadata = s.feature_collection("esensing:focos_bra_2016",
                                       attributes=("id", "municipio", "timestamp", "regiao"),
                                       filter=["timestamp='2016-10-29T17:20:00Z'"],
                                       # filter=["satelite_referencia='true'", "timestamp>='2016-01-01'", "timestamp<'2016-02-01'"],
                                       ts=[
                                           {
                                               'coverage': 'rpth',
                                               'attributes': ('risk', 'temperature', 'humidity', 'precipitation'),
                                               'start_date': '2016-10-29',
                                               'end_date': '2016-10-29'
                                           },
                                           {
                                               'coverage': 'climatologia',
                                               'attributes': ('precipitation')
                                           }
                                       ],
                                       max_features=142)

print(fc, fc_metadata)

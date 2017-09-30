import sys

# to use local version of bdq
sys.path.insert(0, '../src/bdq')

from bdq import bdq

######################################################################################################################
# BDQ Features

b = bdq(wfs="http://localhost:8080/geoserver-esensing/", wtss="http://www.dpi.inpe.br/ts", debug=True)

# Retrieving a selected elements for a given feature
fc, fc_metadata = b.feature_collection("esensing:focos_bra_2016",
                                       attributes=("id", "municipio", "timestamp", "regiao"),
                                       # filter=["satelite_referencia='true'", "timestamp>='2016-01-01'", "timestamp<'2016-02-01'"],
                                       ts=[
                                           {
                                               'coverage': 'rpth',
                                               'attributes': ('risk', 'temperature'),
                                               'start_date': '2016-01-01',
                                               'end_date': '2016-01-01'
                                           },
                                           {
                                               'coverage': 'climatologia',
                                               'attributes': ('precipitation')
                                           }
                                       ],
                                       max_features=3)

print(fc)

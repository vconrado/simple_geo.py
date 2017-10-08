# -*- coding: utf-8 -*-
import sys

# to use local version of simple_geo
sys.path.insert(0, '../src/simple_geo')

from simple_geo import simple_geo as sgeo
from osgeo import ogr

######################################################################################################################
# simple_geo Features

# fazer cache
s = sgeo(wfs="http://localhost:8080/geoserver-esensing/", wtss="http://localhost:7644", debug=False)

print("Features")
# Retrieving the list of all available features in the service
# ft_list = s.list_features()
# print(ft_list)

# ft_desc = s.describe_feature('esensing:municipios')
# print(ft_desc)

# ft_desc = s.describe_feature('esensing:focos_bra_2016')
# print(ft_desc)

#
fc, fc_metadata = s.feature_collection("esensing:estados_bra",
                                       # filter={"nome":'Pernambuco'}, max_features=1)
                                       filter={"nome": 'Santa Catarina'}, max_features=1)

# print(fc_metadata)
# print(fc)
# print(fc.loc[0,'geometry'].wkt)


# print(fc.loc[0, 'geometry'].wkt)
#
# geom = ogr.CreateGeometryFromWkt(fc.loc[0, 'geometry'].wkt)
# print("geom", type(geom))
#
# x = geom.ExportToGML(["FORMAT=GML32"])
# print(x)

# print (fc.loc[0,'geometry'].exportToGML("FORMAT=GML3"))

fc2, fc2_metadata = s.feature_collection("esensing:municipios_bra",
                                         spatial_filter={'within': fc.loc[0, 'geometry'].wkt,
                                                         'intersects': fc.loc[0, 'geometry'].wkt},
                                         max_features=2,
                                         attributes=['nome', 'geom', 'estado'],
                                         sort_by={"nome": "DESC"},  # 'nome', ['nome', 'estado']
                                         filter={"regiao": "S"})

print(fc2_metadata)
print(fc2)

len = s.feature_collection_len("esensing:municipios_bra",
                               spatial_filter={'within': fc.loc[0, 'geometry'].wkt,
                                               'intersects': fc.loc[0, 'geometry'].wkt},
                               filter={"regiao": "S"})

print(len)

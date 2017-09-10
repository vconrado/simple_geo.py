#import sys
#sys.path.append('../src/bdq')

from bdq import bdq

b = bdq("http://localhost:8080/geoserver-esensing/")

ft_list = b.list_features()

print(cv_list)

ft_scheme = b.describe_feature("esensing:focos_bra_2016")

print(cv_scheme)

fc = b.feature_collection("esensing:focos_bra_2016", 
                          attributes=("id","municipio","timestamp"), 
                          within="POLYGON((-49.8929205749999 1.21448026000007,-50.945202767 0.671596891000149,-51.2334818149999 0.0142109470000378,-49.8929205749999 1.21448026000007))", 
                          filter=["vegetacao='2'","(satelite='NPP_375'+OR+satelite='TERRA_M-T')"], 
                          max_features=10)

print(fc)

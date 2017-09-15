# Python Client API for BDQ Web Feature Service (WFS)



## Building and installing bdq.py from source
**1.** In the shell, type
```bash
  git clone https://github.com/vconrado/bdq.py.git
  cd bdq.py/src
  pip install .
```

## Using bdq.py

```python
from bdq import bdq

b = bdq("http://[SERVER_IP]:[PORT]/[GEOSERVER]")

ft_list = b.list_features()

print(cv_list)

ft_scheme = b.describe_feature("esensing:focos_bra_2016")

print(cv_scheme)

# Retrieving all 'focos' of esensing:focos_bra_2016
fc_all = b.feature_collection("esensing:focos_bra_2016")

# Retrieving selected 'focos' of esensing:focos_bra_2016
fc = b.feature_collection("esensing:focos_bra_2016", 
                          attributes=("id","municipio","estado","timestamp"),
                          within="POLYGON((-49.8929205749999 1.21448026000007,-50.945202767 0.671596891000149,-51.2334818149999 0.0142109470000378,-49.8929205749999 1.21448026000007))", 
                          filter=["vegetacao='2'","(satelite='NPP_375'+OR+satelite='TERRA_M-T')"],
                          sort_by=("estado","municipio"),
                          max_features=10)
```


# Python Client API for WFS and WTSS

## Building and installing simple_geo.py from source

1. In the shell, type

```bash


  git clone https://github.com/vconrado/simple_geo.py.git
  cd simple_geo.py/src
  pip install .
```

## Using SimpleGeo.py

### Listing Features and Coverages

In the following example, we import the SimpleGeo module and then create a SimpleGeo object to query and print the list of available features and coverages in the server.



```python
from SimpleGeo import SimpleGeo

# connect to wfs and wtss servers
s = SimpleGeo(wfs="http://wfs_server:8080/geoserver-esensing", wtss="http://wtss_server:7654")

# print available features
print(s.features())

# print available coverages
print(s.coverages())
```

## Getting metadata

In the following example, we use SimpleGeo to retrieve the details of a feature and a coverage. Then we format the response.


```python
import json

# Feature estados_bra
f = s.feature('esensing:estados_bra')
print(f.describe())


# Coverage rpth
c = s.coverage('rpth')
print(c.describe())
```

## Retrieving features

In the following example, we retrieve a feature from the WFS server. SimpleGeo returns a GeoPandasDataFrame with the features.


```python
f = s.feature('esensing:estados_bra')
estados = f.get()
# displaying 
display(estados.head())
```

### Feature methods

- **max_features**: limit the number of features returned
- **sort_by**: sorts by the returning features using one (ou more) attributes
- **attributes**: selects attributes to be retrieved
- **filter**: filtering features by its spatial and non-spatial attributes


In the following example, we retrieve a feature from the WFS server using all allowed options. You can combine then in many ways to select only the features you want.


```python
# import SimpleGeo Predicates
from SimpleGeo import Predicates as pre

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
    
focos = f.get()
display(focos.head())
```

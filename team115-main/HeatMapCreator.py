import zipfile
import requests

import matplotlib.pyplot as plt
import contextily as cx

# import sys
# print(sys.version)
# print(sys.path)

import shapely
import geopandas
import pandas as pd
import scipy.stats

#Read file and plot map
gdf = geopandas.read_file('CalEnviroScreener.geojson')
crs1 = gdf.crs
print("CURRENT CRS", gdf.crs)
df1 = pd.DataFrame(gdf)

readableVariables = [
"ozone", "pm",
"diesel", "pesticide",
"toxicRelease", "traffic",
"asthma", "cardiovascular disease",
"poverty", "unemployment"]

impVariables = {
    "ozone":"L0CalEnviroScreen_3_0_ozoneP",
    "pm":"L0CalEnviroScreen_3_0_pmP",
    "diesel":"L0CalEnviroScreen_3_0_dieselP",
    "pesticide":"L0CalEnviroScreen_3_0_pestP",
    "toxicRelease":"L0CalEnviroScreen_3_0_RSEIhazP",
    "traffic":"L0CalEnviroScreen_3_0_trafficP",
    "asthma" : "L0CalEnviroScreen_3_0_asthmaP",
    "cardiovascular disease": "L0CalEnviroScreen_3_0_cvdP",
    "poverty" : "L0CalEnviroScreen_3_0_povP",
    "unemployment" : "L0CalEnviroScreen_3_0_unempP"
                }


importantVariablesToMean = {}
importantVariablesToSTD = {}
allMeans = df1.mean()
allSTDs = df1.std()

for var in readableVariables:
  #print(var)
  #print(impVariables[var])
  importantVariablesToMean[var] = allMeans[impVariables[var]]
  importantVariablesToSTD[var] = allSTDs[impVariables[var]]

# y < -117.509512
# 33.388512 > x > 33.080434

def getSDNormsFromGDF(gdf):
  objs = 0
  runs = 0
  res = []
  for index, row in gdf.iterrows():
    runs += 1
    #print("fucks", gdf[row])
    #print(list(row["geometry"].exterior.coords))
    #print("HELLO")
    #if row["OBJECTID"] == 2593:
    #  print(list(geo.exterior.coords))
    geo = row["geometry"]
    deadCounty = False
    if type(geo) == shapely.geometry.polygon.Polygon:

      for y, x in list(geo.exterior.coords):
        if x < 32.52498 or x > 33.442806:
          deadCounty = True
          break
          #print(x)
        if y > -116.071939 or y < -117.55:
          #print(y)
          deadCounty = True
          break

    elif type(geo) == shapely.geometry.multipolygon.MultiPolygon:
      #print(geo.bounds)
      minx = geo.bounds[0]
      miny = geo.bounds[1]
      maxx = geo.bounds[2]
      maxy = geo.bounds[3]
      #print(minx, miny, maxx, maxy)
      if minx < 32.52498 or maxx > 33.442806:
        deadCounty = True
      if maxy > -116.071939 or miny < -117.55:
        #print(y)
        deadCounty = True
    #for gdf[index]
    if not deadCounty:
      objs += 1
      dataList = []
      for key in importantVariablesToMean:
        data = row[impVariables[key]]
        #print(key, importantVariablesToMean[key], importantVariablesToSTD[key])
        normed = (scipy.stats.norm(importantVariablesToMean[key],
          importantVariablesToSTD[key]).cdf(data) * 100)
        dataList.append(normed)
        #print(data, normed)
      dataList.append(row["geometry"])
      res.append(dataList)
      #print(key, importantVariablesToMean[key], importantVariablesToSTD[key])
      # print every important mean/variable from here

  print(runs, objs)
  #print(res[0])
  return res


res = getSDNormsFromGDF(gdf)
#for key in importantVariablesToMean:
#  print(key, importantVariablesToMean[key], importantVariablesToSTD[key])



print('ozone, pm, diesal, pesticide, toxicRelease, traffic, asthma, cardiovascularDisease, poverty, or unemployment rates')
input = input()
#Read file and plot map
cols = readableVariables
cols.append("geometry")
df = pd.DataFrame(res, columns = cols)

geodataframe = geopandas.GeoDataFrame(df)
#geodataframe.to_file('shapefile.shp')

#shpframe = geopandas.read_file('shapefile.shp')

#geodataframe.plot(figsize=(15, 7), cmap = 'jet', edgecolor = 'black', column = input, legend=True)
#geoplot = geodataframe.plot(figsize=(15, 7), cmap = 'jet', edgecolor = 'black', column = input, legend=True)
#shpframe.plot(figsize=(15, 7), cmap = 'jet', edgecolor = 'black', column = input, legend=True)

geodataframe.crs = crs1
#Obtain coordinates for shapefiles
#print("JFDSKFJDKSLJFDKLSJF", geodataframe.crs)
geodataframe.crs
df_wm = geodataframe.to_crs(epsg=3857)

#Add background map onto the polygons
ax = df_wm.plot(figsize=(15, 7), alpha=0.5, edgecolor='black', cmap = 'jet', column = input, legend = True)

# newdf = geodataframe.overlay(df_wm, how="union")
# newdf.plot()
cx.add_basemap(ax)

plt.show()
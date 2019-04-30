# -*- coding: utf-8 -*-
import json
import ogr
import geopandas as gpd
import matplotlib.pyplot as plt
import geojson
import os
import requests
from requests.auth import HTTPBasicAuth
import shapely
from shapely.geometry import box, Polygon
import pandas as pd
import gdal

# import the shqpefile of your study site and transform it into a geojson
driver = ogr.GetDriverByName('ESRI Shapefile')
shp_path = "inputs\shp_grasslands\Turnhout_opgekuist_Stien_WGS84_bbox.shp"
file = gpd.read_file(shp_path)
file.to_file("Turnhout2.json", driver="GeoJSON")


with open("Turnhout.json") as f:
    gj = geojson.load(f)
features = gj['features'][0]
  
geometry = {
        "type": "Polygon",
        "coordinates": [
        [
                []
                
        ]
    ]
}
# replace coordinates in the empty json file created above by the actual coordinates from the geojson file
geometry["coordinates"] = features.geometry.coordinates
print(geometry)


# get images that overlap with your study site
geometry_filter = {
        "type": "GeometryFilter",
        "field_name": "geometry",
        "config":geometry
}

# get images acquired within a preset date range
date_range_filter = {
        "type": "DateRangeFilter",
        "field_name": "acquired",
        "config": {
                "gte": "2018-03-01T00:00:00.000Z",
                "lte": "2018-10-31T00:00:00.000Z"
        }
}

# only get images which have < X% cloud coverage
cloud_cover_filter = {
        "type": "RangeFilter",
        "field_name": "cloud_cover",
        "config": {
                "lte": 0.05
    }
}

# combine the geo, date and cloud filters
combined_filter = {
        "type": "AndFilter",
        "config": [geometry_filter, date_range_filter, cloud_cover_filter]
}

# Give API key for ypur Planet account
PLANET_API_KEY = 'c3428a8d40f849a0bf6e59f0c8895919'

item_type = "PSScene4Band"
asset_type = "analytic_sr"

# make API request object
search_request = {
        "interval": "day",
        "item_types":[item_type],
        "filter": combined_filter
}

# Fire off the POST request
search_result= \
requests.post(
        'https://api.planet.com/data/v1/quick-search',
        auth=HTTPBasicAuth(PLANET_API_KEY, ''),
        json=search_request)
print(json.dumps(search_result.json(), indent = 1))

# Extract image properties
image_ids = [feature['id'] for feature in search_result.json()['features']]
image_dates = [feature['properties']['acquired'][0:10] for feature in search_result.json()['features']]
image_months = [feature['properties']['acquired'][5:7] for feature in search_result.json()['features']]
image_days = [feature['properties']['acquired'][8:10] for feature in search_result.json()['features']]
image_clouds = [feature['properties']['cloud_cover'] for feature in search_result.json()['features']]

# Determine overlap between study site and each of the planet scenes
poly_hull = Polygon(geometry["coordinates"][0])
crs = {'init': 'epsg:4326'}
geo_hull = gpd.GeoDataFrame(index=[0], crs=crs, geometry = [poly_hull])  
geo_hull_tr =geo_hull.to_crs({'init': 'epsg:32631'})
hull_area = geo_hull_tr['geometry'].area[0]

df_results = pd.DataFrame(index = range(len(image_ids)), columns=['im_id', 'overlap', 'clouds', 'date', 'month', 'day', 'dekad', 'deviat', 'anal_sr'])
df_results['im_id']= image_ids
df_results['date']= image_dates
df_results['month']= image_months
df_results['day']= image_days
df_results['clouds']= image_clouds
df_results['day'] = df_results['day'].astype('int32')


for x in range(len(image_ids)):
    anal_sr =  'assets.analytic_sr:download' in  search_result.json()['features'][x]['_permissions']
    df_results['anal_sr'][x] = anal_sr
    poly_im = Polygon(search_result.json()['features'][x]['geometry']['coordinates'][0])
    crs = {'init': 'epsg:4326'}
    geo_im = gpd.GeoDataFrame(index=[0], crs=crs, geometry = [poly_im]) 
    geo_im_tr =geo_im.to_crs({'init': 'epsg:32631'})
    geo_inters = geo_im_tr.intersection(geo_hull_tr)
    inters_area = geo_inters.area[0]
    perc_inters = inters_area/hull_area*100
    df_results['overlap'][x] = perc_inters
    if df_results['day'][x]<11:
        df_results['dekad'][x]= 1
        df_results['deviat'][x]= abs(df_results['day'][x]-5)
    elif df_results['day'][x]<21:
        df_results['dekad'][x]= 2
        df_results['deviat'][x]= abs(df_results['day'][x]-15)
    else: 
        df_results['dekad'][x]= 3
        df_results['deviat'][x]= abs(df_results['day'][x]-25)
    
        
    

df_results['overlap'] = df_results['overlap'].astype('float')

# Select only the images with 100% overlap with the study area    
df_results2 = df_results[df_results['overlap']==100]

# Select only the images with downloadable analytic_sr asset
df_results2 = df_results2[df_results2['anal_sr']==True]

# Select only the images with minimum clouds per dekad
def func(group):
    return group.loc[group['clouds'] == group['clouds'].min()]

df_results3 = df_results2.groupby(['month','dekad'], as_index=False).apply(func).reset_index(drop=True)

# Select the image with minimal clouds that is closest to the mid of the dekad
def func2(group):
    return group.loc[group['deviat'] == group['deviat'].min()]

df_results4 = df_results3.groupby(['month','dekad'], as_index=False).apply(func2).reset_index(drop=True)


# Activate the assets that remain in the final results set 
for y in range(len(df_results4)):
    id_item = df_results4['im_id'][y]
    id0_url = 'https://api.planet.com/data/v1/item-types/{}/items/{}/assets'.format(item_type, id_item)
    result = \
    requests.get(
            id0_url,
            auth=HTTPBasicAuth(PLANET_API_KEY, '')
            )
    links = result.json()['analytic_sr']['_links']
    activation_link = links['activate']
    print(activation_link)
    activate_result = \
    requests.get(
            activation_link, 
            auth=HTTPBasicAuth(PLANET_API_KEY, '')
            )
    print(activate_result)
    # Download subarea
    download_url = result.json()[asset_type]['location']
    vsicurl_url = '/vsicurl/' + download_url
    output_file = id_item + '_Damvallei.tif'
    gdal.Warp(output_file, vsicurl_url, dstSRS = 'EPSG:4326', cutlineDSName = "Damvallei.json", cropToCutline = True)

    


    
    
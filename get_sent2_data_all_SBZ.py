# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 10:49:23 2019

@author: stien_heremans
"""

import ogr
from sentinelhub import WmsRequest, WcsRequest, MimeType, CRS, BBox
import datetime
import numpy as np
import matplotlib.pyplot as plt

from sentinelhub import FisRequest, BBox, Geometry, CRS, WcsRequest, CustomUrlParam, \
    DataSource, HistogramType
from sentinelhub.time_utils import iso_to_datetime

INSTANCE_ID = '3afe5624-3087-4641-869f-14e14c9885c9'


input_shp = "inputs\shp_allSBZ\SBZ-Hdeel_Zwin_KH_WGS84.shp"

def plot_image(image, factor=1):
    """
    Utility function for plotting RGB images.
    """
    fig = plt.subplots(nrows=1, ncols=1, figsize=(15, 7))
    if np.issubdtype(image.dtype, np.floating):
        plt.imshow(np.minimum(image * factor, 1))
    else:
        plt.imshow(image)

# Calculate the bounding box of the polygon to be used as the AOI (area of interest
file = ogr.Open(input_shp)
layer = file.GetLayer(0)
for i in range(layer.GetFeatureCount()):
    feature = layer.GetFeature(i) #can be used to create for loop over all polygons in a shapefile
    geometry = feature.GetGeometryRef()
    name = feature.GetFieldAsString(5)
    minLong, maxLong, minLat, maxLat = geometry.GetEnvelope()
    print(name)
    print(minLong, maxLong, minLat, maxLat)
    bbox_coord_WGS84 = [minLong, minLat, maxLong,maxLat]
    bbox_area = BBox((minLong, minLat, maxLong,maxLat),CRS.WGS84)
    output_folder = "outputs/Sen2_data/" + name


# Go to https://apps.sentinel-hub.com/dashboard/#/configurations
# In Simple WMS Instance configuration, add layers with a layer name
# These configurations can be called in the WmsRequest by 'layer= '
# If you just want bands, put 'return[BAND_NAMES]' in the custom script of the layer

#One of the tools in sentinelhub-py package is a wrapper around Sentinel Hub Feature (or Statistical) Info Service (FIS). The service is documented at Sentinel Hub webpage.

    wms_scl_request_2018 = WmsRequest(layer='SCL-S2-L2A',
                                      bbox=bbox_area,
                                      time=('2018-03-01', '2018-10-31'),
                                      maxcc=0.3,
                                      width = 512,
                                      image_format=MimeType.TIFF_d32f)

    wms_scl_img_2018 = wms_scl_request_2018.get_data()

    for index, date in enumerate(wms_scl_request_2018.get_dates()):
        print(index)
        print(date.date())
        good_pix=np.copy(wms_scl_img_2018[index])
        good_pix[(good_pix<=3)] = 0
        good_pix[(good_pix>3) & (good_pix<=6)] = 1
        good_pix[(good_pix>6)] = 0
        perc_good = np.sum(good_pix)/(good_pix.shape[0]*good_pix.shape[1])
        print(perc_good)
        if perc_good >=0.97:
            wms_bands_request = WmsRequest(data_folder=output_folder,
                                       layer='BANDS-S2-L2A',
                                       bbox=bbox_area,
                                       time=date,
                                       width=512,
                                       image_format=MimeType.TIFF_d32f)
            wms_bands_img = wms_bands_request.get_data(save_data=True)
        
    wms_scl_request_2017 = WmsRequest(layer='SCL-S2-L2A',
                               bbox=bbox_area,
                               time=('2017-03-01', '2017-10-31'),
                               maxcc=0.3,
                               width = 512,
                               image_format=MimeType.TIFF_d32f)

    wms_scl_img_2017 = wms_scl_request_2017.get_data()

    for index, date in enumerate(wms_scl_request_2017.get_dates()):
        print(index)
        print(date.date())
        good_pix=np.copy(wms_scl_img_2017[index])
        good_pix[(good_pix<=3)] = 0
        good_pix[(good_pix>3) & (good_pix<=6)] = 1
        good_pix[(good_pix>6)] = 0
        perc_good = np.sum(good_pix)/(good_pix.shape[0]*good_pix.shape[1])
        print(perc_good)
        if perc_good >=0.97:
            wms_bands_request = WmsRequest(data_folder=output_folder,
                                       layer='BANDS-S2-L2A',
                                       bbox=bbox_area,
                                       time=date,
                                       width=512,
                                       image_format=MimeType.TIFF_d32f)
            wms_bands_img = wms_bands_request.get_data(save_data=True)
        
        
        wms_scl_request_2016 = WmsRequest(layer='SCL-S2-L2A',
                               bbox=bbox_area,
                               time=('2016-03-01', '2016-10-31'),
                               maxcc=0.3,
                               width = 512,
                               image_format=MimeType.TIFF_d32f)

    wms_scl_img_2016 = wms_scl_request_2016.get_data()

    for index, date in enumerate(wms_scl_request_2016.get_dates()):
       print(index)
       print(date.date())
       good_pix=np.copy(wms_scl_img_2016[index])
       good_pix[(good_pix<=3)] = 0
       good_pix[(good_pix>3) & (good_pix<=6)] = 1
       good_pix[(good_pix>6)] = 0
       perc_good = np.sum(good_pix)/(good_pix.shape[0]*good_pix.shape[1])
       print(perc_good)
       if perc_good >=0.97:
           wms_bands_request = WmsRequest(data_folder=output_folder,
                                       layer='BANDS-S2-L2A',
                                       bbox=bbox_area,
                                       time=date,
                                       width=512,
                                       image_format=MimeType.TIFF_d32f)
           wms_bands_img = wms_bands_request.get_data(save_data=True)
    
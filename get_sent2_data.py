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
file = ogr.Open("inputs\shp_grasslands\Breemeersen_opgekuist_WGS84_bbox.shp")
layer = file.GetLayer(0)
feature = layer.GetFeature(0)
geometry = feature.GetGeometryRef()
minLong, maxLong, minLat, maxLat = geometry.GetEnvelope()

bbox_coord_WGS84 = [minLong, minLat, maxLong,maxLat]
bbox_area = BBox(bbox=bbox_coord_WGS84, crs=CRS.WGS84)

# Go to https://apps.sentinel-hub.com/dashboard/#/configurations
# In Simple WMS Instance configuration, add layers with a layer name
# These configurations can be called in the WmsRequest by 'layer= '
# If you just want bands, put 'return[BAND_NAMES]' in the custom script of the layer

wms_true_color_request = WmsRequest(layer='TRUE-COLOR-S2-L2A',
                                    bbox=bbox_area,
                                    time=('2016-03-01', '2016-10-31'),
                                    width=512,
                                    maxcc=0.3)

wms_true_color_img = wms_true_color_request.get_data()

print('There are %d Sentinel-2 images available for the growing season of 2016 with cloud coverage less than %1.0f%%.' % (len(wms_true_color_img), wms_true_color_request.maxcc * 100.0))

print('These %d images were taken on the following dates:' % len(wms_true_color_img))
for index, date in enumerate(wms_true_color_request.get_dates()):
    print(' - image %d was taken on %s' % (index, date))

wms_true_color_request = WmsRequest(layer='TRUE-COLOR-S2-L2A',
                                    bbox=bbox_area,
                                    time=('2017-03-01', '2017-10-31'),
                                    width=512,
                                    maxcc=0.3)

wms_true_color_img = wms_true_color_request.get_data()

print('There are %d Sentinel-2 images available for the growing season of 2017 with cloud coverage less than %1.0f%%.' % (len(wms_true_color_img), wms_true_color_request.maxcc * 100.0))

print('These %d images were taken on the following dates:' % len(wms_true_color_img))
for index, date in enumerate(wms_true_color_request.get_dates()):
    print(' - image %d was taken on %s' % (index, date))
    

wms_true_color_request = WmsRequest(layer='TRUE-COLOR-S2-L2A',
                                    bbox=bbox_area,
                                    time=('2018-03-01', '2018-10-31'),
                                    width=512,
                                    maxcc=0.3)

wms_true_color_img = wms_true_color_request.get_data()

print('There are %d Sentinel-2 images available for the growing season of 2018 with cloud coverage less than %1.0f%%.' % (len(wms_true_color_img), wms_true_color_request.maxcc * 100.0))

print('These %d images were taken on the following dates:' % len(wms_true_color_img))
for index, date in enumerate(wms_true_color_request.get_dates()):
    print(' - image %d was taken on %s' % (index, date))
    
    

wms_bands_request = WmsRequest(layer='BANDS-S2-L2A',
                               bbox=bbox_area,
                               time='2018-05-06',
                               width=512,
                               image_format=MimeType.TIFF_d32f)

wms_bands_img = wms_bands_request.get_data()
    
plot_image(wms_bands_img[-1][:, :, 11])



wms_clouds_request = WmsRequest(layer='SCL-S2-L2A',
                               bbox=bbox_area,
                               time='2018-05-06',
                               width=512,
                               image_format=MimeType.TIFF_d32f)

wms_clouds_img = wms_clouds_request.get_data()
    
plot_image(wms_clouds_img[-1])




wms_bands_request = WmsRequest(layer='BANDS-S2-L2A',
                               bbox=bbox_area,
                               time='latest',
                               width=512,
                               image_format=MimeType.TIFF_d32f)

wms_bands_img = wms_bands_request.get_data()
    
plot_image(wms_bands_img[-1][:, :, 11])



wms_clouds_request = WmsRequest(layer='SCL-S2-L2A',
                               bbox=bbox_area,
                               time='latest',
                               width=512,
                               image_format=MimeType.TIFF_d32f)

wms_clouds_img = wms_clouds_request.get_data()
    
plot_image(wms_clouds_img[-1])

wms_bands_request = WmsRequest(data_folder='outputs\Sen2_data',
                               layer='BANDS-S2-L2A',
                               bbox=bbox_area,
                               time='2018-05-06',
                               width=512,
                               image_format=MimeType.TIFF_d32f)
wms_bands_img = wms_bands_request.get_data(save_data=True)



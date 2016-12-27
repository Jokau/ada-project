import requests
import json

import numpy as np
import pandas as pd

def import_data():
	data = []
	offset = 0
	continue_=True

	while(continue_):
		print(offset)
        query='https://api3.geo.admin.ch/rest/services/all/MapServer/identify?geometry=446000.0000000001,37750,860500.0000000002,317750.00000000006&geometryFormat=geojson&geometryType=esriGeometryEnvelope&imageDisplay=1536,759,96&lang=fr&layers=all:ch.astra.unfaelle-personenschaeden_getoetete&mapExtent=276000,250,1044000,379750&offset={0}&returnGeometry=true&tolerance=5'.format(offset)
		
		r=requests.get(query)

	    json_data=(json.loads(str(r.text))).get('results')

	    if(len(data) == 0):
	    	#no more data to scrape
	    	continue_=False
	    else :
	    	offset+=200

	    	data.append(json_data) #merge two lists into one


    return data


#Remove all items we are not interested in
def clean_data(data_list):
    
    
    data_list_copy = data_list.copy()
    for item in data_list_copy : 
        properties = item.get('properties')
        del properties['accidentday_de']
        del properties['accidentday_it']
        del properties['accidenttype_de']
        del properties['accidenttype_it']
        del properties['severitycategory_it']
        del properties['severitycategory_de']
        
        
    return data_list_copy


#reformat data so we have each property as a feature of the event
def reformat_data(data_list):
    data_list_reformat = []
    
    for item in data_list:
        properties = item.get('properties')
        del item['properties']
        item = dict(item, **properties)
        data_list_reformat.append(item)
    
    return data_list_reformat
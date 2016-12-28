import requests
import json
import copy

import goslate

import numpy as np
import pandas as pd

def import_data(all_data = False):
    layers =["ch.astra.unfaelle-personenschaeden_alle",
             "ch.astra.unfaelle-personenschaeden_getoetete",
             "ch.astra.unfaelle-personenschaeden_fussgaenger",
             "ch.astra.unfaelle-personenschaeden_fahrraeder",
             "ch.astra.unfaelle-personenschaeden_motorraeder"]
    data = []

    if ~all_data:
        for layer in layers :

            offset = 0
            continue_=True

            print("Processing layer : {}".format(layer))
            layer_items = []

            while(continue_):
                query='https://api3.geo.admin.ch/rest/services/all/MapServer/identify?geometry=446000.0000000001,37750,860500.0000000002,317750.00000000006&geometryFormat=geojson&geometryType=esriGeometryEnvelope&imageDisplay=1536,759,96&lang=fr&layers=all:{}&mapExtent=276000,250,1044000,379750&offset={}&returnGeometry=true&tolerance=5'.format(layer, offset)
                #query='https://api3.geo.admin.ch/rest/services/all/MapServer/identify?geometry=446000.0000000001,37750,860500.0000000002,317750.00000000006&geometryFormat=geojson&geometryType=esriGeometryEnvelope&imageDisplay=1536,759,96&lang=fr&layers=all:ch.astra.unfaelle-personenschaeden_getoetete&mapExtent=276000,250,1044000,379750&offset={0}&returnGeometry=true&tolerance=5'.format(offset)

                r=requests.get(query)

                json_data=(json.loads(str(r.text))).get('results')

                if(len(json_data) == 0):
                    #no more data to scrape
                    continue_=False
                else :
                    #set offset to the beginning of the next file to import
                    offset+=200
                    layer_items+=json_data #merge two lists into one

                if(~all_data):
                    break
                    
            print("Layer processed : {} records\n".format(len(layer_items)))
            data += layer_items
            if(~all_data):
                break    
            
        print("Whole dataset processed : {} records\n".format(len(data)))

    # else:
    #     url_0="https://api3.geo.admin.ch/rest/services/all/MapServer/identify?geometry=446000.0000000001,37750,860500.0000000002,317750.00000000006&geometryFormat=geojson&geometryType=esriGeometryEnvelope&imageDisplay=1536,759,96&lang=fr&layers=all:ch.astra.unfaelle-personenschaeden_getoetete&mapExtent=276000,250,1044000,379750&returnGeometry=true&tolerance=5"
    #     url_1="https://api3.geo.admin.ch/rest/services/all/MapServer/identify?geometry=446000.0000000001,37750,860500.0000000002,317750.00000000006&geometryFormat=geojson&geometryType=esriGeometryEnvelope&imageDisplay=1536,759,96&lang=fr&layers=all:ch.astra.unfaelle-personenschaeden_getoetete&mapExtent=276000,250,1044000,379750&offset=200&returnGeometry=true&tolerance=5"
    #     r0=requests.get(url_0)
    #     r1=requests.get(url_1)
    #     json_data0=(json.loads(str(r0.text))).get('results')
    #     json_data1=(json.loads(str(r1.text))).get('results')
    #     data = json_data0+json_data1

    return data

#preprocess each item in the dataset
def preprocess_data(data_list):
    data_preprocessed = []
    data_list_copy = copy.deepcopy(data_list)

    #apply each preprocessing function on each item of the dataset
    for item in data_list :
        item = (reformat_item(clean_item(item)))
        data_preprocessed.append(item)

    return data_preprocessed

#Remove item we are not interested in
def clean_item(item):
    if 'properties' in item:
        properties = item.get('properties')
        del properties['accidentday_de']
        del properties['accidentday_it']
        del properties['accidenttype_de']
        del properties['accidenttype_it']
        del properties['severitycategory_it']
        del properties['severitycategory_de']
        #print("prop")
        
    return item


#reformat data so we have each property as a feature of the event
def reformat_item(item):
    data_list_reformat = []
    
    if 'properties' in item:
        properties = item.get('properties')
        del item['properties']
        item = dict(item, **properties)
        #print("prop")

    if 'geometry' in item:
        coords = (item.get('geometry')).get('coordinates')
        del item['geometry']
        item = dict(item, **{'coordinates' : coords})
        #print("geo")
    
    return item

#Translation worked the first but returned HTTP Error 503: Service Unavailable afterwards
#do not use for now
def translate_item(item):
    data_list_translate = []
    gs= goslate.Goslate()    

    if 'label' in item:
        translation = gs.translate(item['label'], "fr")
        if(item['label'==translation]):
            with open("logs/translate_log.txt", "a") as text_file:
                text_file.write("Failed to translate {}\n".format(translation))
        del item['label']
        item = dict(item, **{'label' : translation})
        print("Translating label {}".format(translation))

    return item
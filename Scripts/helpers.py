import requests
import json
import copy
import datetime
import urllib

import goslate

import numpy as np
import pandas as pd

def import_data(all_data):
    layers =["ch.astra.unfaelle-personenschaeden_alle",
             "ch.astra.unfaelle-personenschaeden_getoetete",
             "ch.astra.unfaelle-personenschaeden_fussgaenger",
             "ch.astra.unfaelle-personenschaeden_fahrraeder",
             "ch.astra.unfaelle-personenschaeden_motorraeder"]    
    data = []

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

            #For testing, we only take a sample of the dataset, with 603 records per layer
            if(all_data==False):
                if (offset ==800):    
                   break
               
        print("Layer processed : {} records\n".format(len(layer_items)))
        data += layer_items 
    if(all_data):    
        print("Whole dataset processed : {} records\n".format(len(data)))
    else:
        print("Sample dataset processed : {} records\n".format(len(data)))

    return data

#preprocess each item in the dataset
def preprocess_data(data_list):
    data_preprocessed = []
    data_list_copy = copy.deepcopy(data_list)
    date_time = datetime.datetime.now().strftime("%Y-%m-%d-%Hh%M")
    path_log = "logs/preprocessing_logs/{}.txt".format(date_time)
    with open(path_log, "w") as text_file:
                    text_file.write("Preprocessing Error log on {}\n"
                        .format(date_time))

    #apply each preprocessing function on each item of the dataset
    for item in data_list :
        item = clean_item(item, path_log)
        item = reformat_item(item, path_log)
        #item = translate_item(item, path_log)
        data_preprocessed.append(item)

    return data_preprocessed

#Remove item we are not interested in
def clean_item(item, log):
    if 'properties' in item:
        properties = item.get('properties')
        del properties['accidentday_de']
        del properties['accidentday_it']
        del properties['accidenttype_de']
        del properties['accidenttype_it']
        del properties['severitycategory_it']
        del properties['severitycategory_de']
        del properties['roadtype_de']
        del properties['roadtype_it']
    if 'bbox' in item : 
        del item['bbox']
    if 'type' in item:
        del item['type']
    if 'featureId' in item:
        del item['featureId']
    if 'geometryType' in item:
        del item['geometryType']     
    if 'layerBodId' in item:
        del item['layerBodId']            

    return item


#reformat data so we have each property as a feature of the event
def reformat_item(item, log):
    data_list_reformat = []
    
    if 'properties' in item:
        properties = item.get('properties')
        del item['properties']
        item = dict(item, **properties)

    if 'geometry' in item:
        coords = (item.get('geometry')).get('coordinates')
        del item['geometry']
        item = dict(item, **{'coordinates' : coords[0]})

    if 'accidentday_fr' in item:
        #print(item['accidentday_fr'][0])
        day, time, month_year = (item['accidentday_fr']).split(" / ", 3)
        month, year = month_year.split(" ", 2)
        del item['accidentday_fr']
        item = dict(item, **{'day' : day})
        item = dict(item, **{'time' : time})
        item = dict(item, **{'month' : month})
    
    return item

#Translation worked the first but returned HTTP Error 503: Service Unavailable afterwards
#do not use for now
def translate_item(item, log):
    data_list_translate = []
    gs= goslate.Goslate()    
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if 'label' in item:
        try:
            translation = gs.translate(item['label'], "fr")
            if(item['label']==translation):
                with open(log, "a") as text_file:
                    text_file.write("{} : Failed to translate {}\n"
                        .format(date_time, translation))
            del item['label']
            item = dict(item, **{'label' : translation})
            print("Translating label {}".format(translation))
        except urllib.error.HTTPError as e:
            with open(log, "a") as text_file:
                    text_file.write("{} : Failed to translate {} due to {}\n"
                        .format(date_time, item['label'], e))

    return item

#found on http://python.jpvweb.com/mesrecettespython/doku.php?id=combinaisons
def combinliste(seq, k=2):
    p = []
    i, imax = 0, 2**len(seq)-1
    while i<=imax:
        s = []
        j, jmax = 0, len(seq)-1
        while j<=jmax:
            if (i>>j)&1==1:
                s.append(seq[j])
            j += 1
        if len(s)==k:
            p.append(s)
        i += 1 
    return p

def generate_feature_combinations(feats, size):
    combinations = []    
    for i in range(size+1):
        #print(i)
        combinations.append(combinliste(feats, i))
        
    return combinations


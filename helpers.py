import collections
import datetime
import goslate
import json
import requests
import urllib


def import_data():
    query_url = 'https://api3.geo.admin.ch/rest/services/all/MapServer/identify?geometry=446000.0000000001,37750,860500.0000000002,317750.00000000006&geometryFormat=geojson&geometryType=esriGeometryEnvelope&imageDisplay=1536,759,96&lang=fr&layers=all:{0}&mapExtent=276000,250,1044000,379750&offset={1}&returnGeometry=true&tolerance=5'
    layers = ["ch.astra.unfaelle-personenschaeden_alle",
              "ch.astra.unfaelle-personenschaeden_getoetete",
              "ch.astra.unfaelle-personenschaeden_fussgaenger",
              "ch.astra.unfaelle-personenschaeden_fahrraeder",
              "ch.astra.unfaelle-personenschaeden_motorraeder"]
    data = list()

    for layer in layers:
        print("Scraping layer {0}".format(layer))
        finished = False
        offset = 0
        layer_data = list()
        while not finished:
            r = requests.get(query_url.format(layer, offset))
            json_data = json.loads(r.text).get('results')
            if len(json_data) == 0:
                finished = True
            else:
                offset += 200
                layer_data += json_data
        print("Layer scraped : {0} records".format(len(layer_data)))
        data += layer_data

    print("Scraped data: {0} records".format(len(data)))
    return data


def flatten(d, parent_key='', sep='_'):
    """As seen in http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys"""
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# Translation worked the first but returned HTTP Error 503: Service Unavailable afterwards
# do not use for now
def translate_item(item, log):
    data_list_translate = []
    gs = goslate.Goslate()
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if 'label' in item:
        try:
            translation = gs.translate(item['label'], "fr")
            if (item['label'] == translation):
                with open(log, "a") as text_file:
                    text_file.write("{} : Failed to translate {}\n"
                                    .format(date_time, translation))
            del item['label']
            item = dict(item, **{'label': translation})
            print("Translating label {}".format(translation))
        except urllib.error.HTTPError as e:
            with open(log, "a") as text_file:
                text_file.write("{} : Failed to translate {} due to {}\n"
                                .format(date_time, item['label'], e))

    return item


# found on http://python.jpvweb.com/mesrecettespython/doku.php?id=combinaisons
def combinliste(seq, k=2):
    p = []
    i, imax = 0, 2 ** len(seq) - 1
    while i <= imax:
        s = []
        j, jmax = 0, len(seq) - 1
        while j <= jmax:
            if (i >> j) & 1 == 1:
                s.append(seq[j])
            j += 1
        if len(s) == k:
            p.append(s)
        i += 1
    return p


def generate_feature_combinations(feats, size):
    combinations = []
    for i in range(size + 1):
        # print(i)
        combinations.append(combinliste(feats, i))

    return combinations

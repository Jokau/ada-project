import matplotlib
import matplotlib.pyplot as plt
import datetime
import pandas as pd
from Scripts.helpers import *
import pprint
import os

def plot_all_features(data, exclusion_list = ['fsocommunecode', 'type', 'layerBodId', 'geometryType', 'featureId', 'bbox', 'accidentday_fr', 'coordinates']):
    date_time = datetime.datetime.now().strftime("%Y-%m-%d-%Hh%M")
    path_log = "logs/plot_logs/{}.txt".format(date_time)

    with open(path_log, "w") as text_file:
                    text_file.write("Plot Error log on {}\n"
                        .format(date_time))

    print("Plotting all features")
    for feature in data:
        if feature not in exclusion_list:
            plot_feature(data, feature, date_time)
    print("-> Done plotting")


#plot every possible combination of features in the data of a given size, except the features in the exclusion list
def plot_all_feature_combinations(data, exclusion_list=['fsocommunecode', 'type', 'layerBodId', 'geometryType', 'featureId', 'bbox', 'accidentday_fr', 'coordinates'], size=0):
    print("***Generating feature combinations***")
    features = list(set(data.columns) - set(exclusion_list))

    if(size == 1):
        print("-> Done")
        plot_all_features(data)
    else:   
        feature_combinations = generate_feature_combinations(features, size)
        print("-> Done")
    
        print("***Plotting feature combinations***")

        for combinations in feature_combinations:
            for combination in combinations:
                if len(combination)>1:
                    plot_feature_combination(data, combination, False)

        print("-> Done")

#plot the combination of features given as a parameter
def plot_feature_combination(df, features, verbose=False):
    data = df.copy()
    dir_ = "Resources/plots/{}-features".format(len(features))    

    column=""+features[0]
    value=""+data[features[0]].astype(str)

    font = {'family' : 'monospace',
        'weight' : 'normal',
        'size'   : 5}

    fig, ax = plt.subplots()
    fig.set_size_inches(15, 10)

    matplotlib.rc('font', **font)
    
    for feature in features:
        if(feature != features[0]):
            column+="_"+feature
            value+="_"+data[feature].astype(str)
    
    data[column] = value
    
    df = (data.groupby(column).count())['canton']
    
    title = "Number of events per {}".format(column)       

    df.plot(kind='bar', stacked=False)

    plt.xlabel(column)
    plt.ylabel("Number of events")
    plt.title(title)
    plt.xticks(rotation=70)

    if not os.path.exists(dir_):
        os.makedirs(dir_)

    plt.savefig("{}/{}.png".format(dir_,title), dpi=200)
    plt.close()
    if(verbose):
        print("-> Done plotting {}".format(column))


def plot_feature(df, feature, date):
    data = df.copy()
    path_log = "logs/plot_logs/{}.txt".format(date)    

    dir_ = "Resources/plots/1-feature"

    font = {'family' : 'monospace',
        'weight' : 'normal',
        'size'   : 5}

    fig, ax = plt.subplots()
    fig.set_size_inches(15, 10)

    matplotlib.rc('font', **font)

#    dont_plot = ['type', 'layerBodId', 'geometryType', 'featureId', 'bbox', 'accidentday_fr']
    not_plotted_features = list(set(data.columns.values) - set(feature))

    title = "Number of events per {}".format(feature)        


#    if feature not in dont_plot:
    print("plotting feature {}".format(feature))

    try:    
        column = not_plotted_features[0]
        accident_type_stats = (data.groupby(feature).count())[column]
    except TypeError as e:
        print("->    Type Error : {}".format(e))
        with open(path_log, "a") as text_file:
            text_file.write("{} : Failed to plot {} due to {}\n"
                .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),feature, e))
        return
    except KeyError as e1:
        print("->    Key Error : {}".format(e1))    
        column = not_plotted_features[1]
        accident_type_stats = (data.groupby(feature).count())[column]

    accident_type_stats.plot(kind='bar', stacked=False)


    plt.xlabel(feature)
    plt.ylabel("Number of events")
    plt.title(title)
    plt.xticks(rotation=70)
    #plt.rc('xtick', labelsize=45)

    if not os.path.exists(dir_):
        os.makedirs(dir_) 


    plt.savefig("{}/{}.png".format(dir_,title), dpi=200)
    plt.close()
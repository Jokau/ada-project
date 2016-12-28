import matplotlib
import matplotlib.pyplot as plt
import datetime
import pandas as pd

def plot_all_features(data):
    date_time = datetime.datetime.now().strftime("%Y-%m-%d-%Hh%M")
    path_log = "logs/plot_log-{}.txt".format(date_time)

    dont_plot = ['fsocommunecode', 'type', 'layerBodId', 'geometryType', 'featureId', 'bbox', 'accidentday_fr']


    with open(path_log, "w") as text_file:
                    text_file.write("Plot Error log on {}\n"
                        .format(date_time))

    print("Plotting all features")
    for feature in data:
    	if feature not in dont_plot:
        	plot_feature(data, feature, date_time)
    print("Done plotting")


def plot_feature_combination(data, features):
    column=""
    value=""
    
    for feature in features :
        column+=feature
        value+=data[feature].astype(str)
    
    data[column] = value
    
    df = (data.groupby(column).count())['canton']
    
    print("Plotting features : {}".format(features))
    title = "events_per_{}".format(column)

    df.plot(kind='bar', stacked=False)

    plt.xlabel(column)
    plt.ylabel("Number of events")
    plt.title(title)
    plt.xticks(rotation=70)

    plt.savefig("Resources/plots/{}.png".format(title), dpi=200)

    print("Done plotting {}".format(features))


def plot_feature(data, feature, date):
    path_log = "logs/plot_log-{}.txt".format(date)    
    font = {'family' : 'monospace',
        'weight' : 'normal',
        'size'   : 5}

    fig, ax = plt.subplots()
    fig.set_size_inches(15, 10)

    matplotlib.rc('font', **font)

#    dont_plot = ['type', 'layerBodId', 'geometryType', 'featureId', 'bbox', 'accidentday_fr']
    not_plotted_features = list(set(data.columns.values) - set(feature))

    title = "events_per_{}".format(feature)        


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


    plt.savefig("Resources/plots/{}.png".format(title), dpi=200)
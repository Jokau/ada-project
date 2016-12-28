import matplotlib.pyplot as plt


def plot_feature(data, feature='accidenttype_fr'):

    dont_plot = ['type', 'layerBodId', 'geometryType', 'featureId', 'bbox']
    not_plotted_features = list(set(data.columns.values) - set(feature))

    title = "events_per_{}".format(feature)


    if feature not in dont_plot:
        print("plotting feature {}".format(feature))

        try:    
            column = not_plotted_features[0]
            accident_type_stats = (data.groupby(feature).count())[dont_plot[0]]
        except TypeError as e:
            print("->    Error")
            with open("logs/plot_log.txt", "a") as text_file:
                text_file.write("Failed to plot {} due to {}\n".format(feature, e))
            return
        except KeyError as e1:
            print("->    Error")    
            column = not_plotted_features[1]
            accident_type_stats = (data.groupby(feature).count())[column]

        accident_type_stats.plot(kind='bar', stacked=True)


        plt.xlabel(feature)
        plt.ylabel("Number of events")
        plt.title(title)
        plt.xticks(rotation=35)

        plt.savefig("Resources/plots/{}.png".format(title), dpi=199)
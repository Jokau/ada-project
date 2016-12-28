import matplotlib.pyplot as plt


def plot_feature(data, feature='accidenttype_fr'):
    not_plotted_features = list(set(data.columns.values) - set(feature))
    title = "events_per_{}".format(feature)
    
    try:    
        column = not_plotted_features[0]
        accident_type_stats = (data.groupby(feature).count())[column]
    except TypeError as e:
        with open("logs/plot_log.txt", "a") as text_file:
            text_file.write("Failed to plot {} due to {}\n".format(feature, e))
        return
    except KeyError as e1:
        column = not_plotted_features[1]
        accident_type_stats = (data.groupby(feature).count())[column]

    accident_type_stats.plot(kind='bar', stacked=True)


    plt.xlabel(feature)
    plt.ylabel("Number of events")
    plt.title(title)

    plt.savefig("Resources/plots/{}.png".format(title))
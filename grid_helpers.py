import collections
import datetime
import goslate
import json
import requests
import urllib
import math
import numpy as np

def create_count_grid(square_size, df):
    
    xRange=840000-480000
    yRange=300000-70000
    """
    Creates and fills an array with the count of accidents per squares
    of size square_size on the map with the provided DataFrame df.
    """
    nb_x = math.ceil(xRange/square_size)
    nb_y = math.ceil(yRange/square_size)
    
    grid = np.zeros((nb_x, nb_y))
    #print(nb_x, nb_y, square_size, grid.shape)
    
    for index, row in df.iterrows():
        x = math.floor((row['geometry_coordinates'][0] - 480000) / square_size)
        y = math.floor((row['geometry_coordinates'][1] - 70000) / square_size)
        grid[x, y] += 1
    return grid


def compute_ratio(grid):
    """
    To find a good square size length, we compute a ratio that is (% of non empty squares)/(mean of non zero values)
    """
    non_empty_indices = np.nonzero(grid)
    grid_non_zero = grid[non_empty_indices]
    
    non_empty_pct = len(non_empty_indices) / (grid.shape[0] * grid.shape[1])
    
    mean = grid.mean()
    mean_non_zero = grid_non_zero.mean()
    
    return non_empty_pct / mean_non_zero, non_empty_pct / mean


def optimality_plot(df):
    """
    Plot the result of the ratio per square length
    """
    return [[i, compute_ratio(create_count_grid(i, df))] for i in range (500, 15000, 1000)]


def create_grid_per_year(all_data_df, square_size=1000):
    grid_count_list = list()
    years = [2011, 2012, 2013, 2014, 2015]
    for year in years:
        filterer_year_df = all_data_df[all_data_df['year'] == year]
        year_grid = create_count_grid(square_size, filterer_year_df)
        grid_count_list.append(year_grid)
    return grid_count_list

#Compute the coordinates of each corner of the square area based on the coordinates
#of the lower left corner of the area.
def find_surrounding_points(x, y, square_size):
    x2 = x+square_size
    y2 = y
    
    x3 = x2
    y3 = y+square_size
    
    x4 = x
    y4 = y3

    return x2, y2, x3, y3, x4, y4

#Compute the GPS coordinates of the square area.
def find_square_coords(point_coords, square_size=1000):
    xOffset = 480000
    yOffset = 70000
    
    x1 = point_coords[0]*square_size + xOffset
    y1 = point_coords[1]*square_size + yOffset
    
    x2, y2, x3, y3, x4, y4 = find_surrounding_points(x1, y1, square_size)
    
    p1 = ch1903_to_wgs84(x1, y1)
    p2 = ch1903_to_wgs84(x2, y2)
    p3 = ch1903_to_wgs84(x3, y3)
    p4 = ch1903_to_wgs84(x4, y4)
    
    return p1, p2, p3, p4

#This function generates a geojson polygon for a square area computed using the 
#coordinates of the lower left corner of the area.
def generate_goejson_polygon(point, year):
    p1, p2, p3, p4 = find_square_coords(point)
    s='''{ "type": "Polygon", "year":%d,
    "coordinates": [
        [ [%3f, %3f], [%3f, %3f], [%3f, %3f], [%3f, %3f], [%3f, %3f] ]
      ]
   }\n'''%(year, p1[1], p1[0], p2[1], p2[0], p3[1], p3[0], p4[1], p4[0], p1[1], p1[0])
    return s


#This function generates a goejson file describing the locations of the areas with
#the highest variances in the number of accidents between two consecutive years.
def goejson_highest_variance_areas(df, threshold=5):
    year_grids = create_grid_per_year(df)
    comp_grids = [np.abs(year_grids[i] - year_grids[i+1]) for i in range(len(year_grids) - 1)]

    polygons='''{
      "type": "Feature",    
      "geometry": {
        "type": "GeometryCollection",    
        "geometries": ['''
    year=2012

    for i in range(len(comp_grids)):
        x=comp_grids[i]
        where = np.where(x > x.max() - threshold)
        if(i!=0):
            polygons+=','

        for j in range(len(where)):
            if(j!=0):
                polygons+=','
            polygons+=(generate_goejson_polygon(where[j], year))
        
        year+=1

    polygons+=''']
      },
      "properties": {
        "name": "null island"
      }
    }'''

    polygons=polygons.replace('\n', "")

    with open("data/high_variance_areas.json", "w") as text_file:
                    text_file.write(polygons)



### DEPRECATED ####
#This function generates goejson files describing the locations of the areas with
#the highest variances in the number of accidents between two consecutive years.
def find_highest_variance_areas(comp_grids, threshold=5):
    
    year=2012
    
    for x in comp_grids:
        where = np.where(x > x.max() - threshold)
        generate_geojson(where, year)
        year+=1

#This function computes the GPS coordinates based on the Swiss coordinates
def ch1903_to_wgs84(east, north):
    # Convert origin, where Bern is 0,0
    east -= 600000
    north -= 200000
    east /= 1000000
    north /= 1000000
    # Calculate longitude and latitude in 10000" units
    lon = 2.6779094
    lon += 4.728982 * east
    lon += 0.791484 * east * north
    lon += 0.1306 * east * north * north
    lon -= 0.0436 * east * east * east
    lat = 16.9023892
    lat += 3.238272 * north;
    lat -= 0.270978 * east * east
    lat -= 0.002528 * north * north
    lat -= 0.0447 * east * east * north
    lat -= 0.0140 * north * north * north
    # Convert longitude and latitude back in degrees.
    lon *= 100 / 36
    lat *= 100 / 36
    return [lat, lon]
        
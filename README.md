#ADA Project
Ireneu Pla, Ismaïl Imani & Joël Kaufmann

##Abstract
The project’s goal is to extract the maximum amount of information from the traffic accidents in Switzerland between 2011 and 2016, based on the data provided in http://map.donneesaccidents.ch/.
What we have in mind is to extract:

-        The high concentration accidents areas
-        The correlation between accidents and places (e.g. alcohol related accidents in Valais)
-        The link between accidents and seasons/weather conditions
-       The link between the day of the week and accidents
-        Find anomalies: sudden changes (no more accidents/new cases) and link them with external data like road configuration changes (Google Earth?, TBD)
-        Create a visualization
 
## Data description
The base data set is a visualization layer of the accidents in Switzerland provided by the Federal Roads Office (OFRU) on the map.geo.admin.ch swisstopo map.
There are several layers (deadly accidents, with motorcycles, bicycles, pedestrians, ...) and each accident is shown as a dot on the map and is linked to detailed JSON information, for example:
<ul>
coordinates: [[692392.0, 186750.0]]<br/>
layerName: Accidents mortels<br/>
severitycategory_fr: accident avec tués<br/>
accidentyear: 2015<br/>
accidentday_fr: lundi / 08h-09h / décembre 2015<br/>
roadtype_fr: route principale<br/>
accidenttype_fr: dérapage ou perte de maîtrise<br/>
</ul>


We are trying to obtain a bigger raw set from the OFS.


## Feasibility and Risks
We’ve already seen how to retrieve the data from the map. The JSON data related to each accident can be automatically retrieved with queries.
 
Our main fear is to work on a data set that is very small (about 100’000 entries) and not on a very long period (6 years) to have reliable results. We hope the OFS can provide us a bigger set.
Create correct area clusters of accidents overall the swiss map may be a tough task.
We have not found yet a detailed enough map to see the road configuration changes through time and might not be able to find one.
 
It is also important for us to do a useful work that is not a copy of the current visualization.
 
## Deliverables
Geographical representation of the different extractable information (number, causes, severity, ...)


## Time plan
-> 6.11 - 19.11: Data importation, parsing, cleaning<br/>
-> 20.11 - 3.12: Clusters, region information<br/>
-> 3.12 – 17.12 (Checkpoint): data analysis based on type, time, …<br/>
-> 17.12- end January: visualization<br/>

# Apologies in advance for a lot of commented out stuff, preparing it for my project!

import urllib.request, urllib.error, urllib.parse, json
from flask import Flask, render_template, request
import time
import mapsKey as mapsKey

app = Flask(__name__)
base_url = "https://bikewise.org/api/v2/"

def safe_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print(url)
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print(url)
        print("Reason: ", e.reason)
    return None

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def getData(url):
    result = safe_get(url)
    if result is not None:
        return json.load(result)

## convert address, zip, etc into lat/lng to center on map
def convertLoc(proximity):
    mapBaseUrl = "https://maps.googleapis.com/maps/api/geocode/json?"
    params = {}
    params["address"] = proximity
    params["key"] = mapsKey.key
    mapUrl = mapBaseUrl + urllib.parse.urlencode(params)
    # print(mapUrl)
    return mapUrl

# convertLoc("Texas")

def getThefts(
    proximity = "Seattle",
    incident_type = "theft",
    params={},
    ):
    params["proximity"] = proximity
    params["incident_type"] = incident_type
    url = base_url + "incidents?" + urllib.parse.urlencode(params)
    geoLoc = base_url + "locations/markers?" + urllib.parse.urlencode(params)
    url = url.lower() #because capitalization ruins the API call
    geoLoc = geoLoc.lower()

    theftData = getData(url)
    locData = getData(geoLoc)
    mapData = getData(convertLoc(proximity))
    if theftData is not None:
        # return render_template("index.html", theftData=theftData, locData=locData, incident=incident_type, loc=proximity)
        return render_template("index.html", theftData=theftData, locData=locData, mapData=mapData, loc=proximity)
    else: 
        return render_template("index.html", prompt="Something went wrong. Please try again later.") 

def getIncidents(
    # per_page = "10",
    proximity = "Seattle",
    incident_type = "theft",
    # proximity_square = "100",
    query = "",
    params={},
    ):
    # params["per_page"] = per_page
    params["proximity"] = proximity
    params["incident_type"] = incident_type
    # params["proximity_square"] = proximity_square
    params["query"] = query
    url = base_url + "incidents?" + urllib.parse.urlencode(params)
    geoLoc = base_url + "locations/markers?" + urllib.parse.urlencode(params)
    url = url.lower() #because capitalization ruins the API call
    geoLoc = geoLoc.lower()

    theftData = getData(url)
    locData = getData(geoLoc)
    mapData = getData(convertLoc(proximity))
    if theftData is not None:
        # return render_template("index.html", theftData=theftData, locData=locData, incident=incident_type, loc=proximity)
        return render_template("index.html", theftData=theftData, locData=locData, mapData=mapData, loc=proximity, query=query, incident_type=incident_type)
    else: 
        return render_template("index.html", prompt="Something went wrong. Please try again later.") 

## ROUTE
@app.route("/", methods=["GET", "POST"])
def main_handler():
    if request.method == "POST":
        proximity = request.form.get("loc")
        search = request.form.get("query")
        incident_type = request.form.get("incident")

        if proximity and search and incident_type:
            return getIncidents(proximity, incident_type, search)
        elif proximity and search:
            return getIncidents(proximity, query=search)
        elif proximity and incident_type: 
            return getIncidents(proximity, incident_type)
        elif proximity:
            return getThefts(proximity)
        else:
            return render_template("index.html", prompt="Please input a location.")
    else:
        return render_template("index.html")

## about page
@app.route("/about")
def about():
    return render_template("about.html")

## convert unix timestamp to readable format
@app.template_filter("ctime")
def timectime(unix):
    return time.ctime(unix) # datetime.datetime.fromtimestamp(s)

if __name__ == "__main__":
    # Used when running locally only. 
	# When deploying to Google AppEngine, a webserver process will
	# serve your app. 
    app.run(host="localhost", port=8080, debug=True)
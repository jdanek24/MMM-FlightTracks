# MMM-FlightTracks

## About

MMM-FlightTracks is a flight tracking module for [MagicMirror](https://github.com/MagicMirrorOrg/MagicMirror/). The flight tracking functionality is implemented in Python, allowing it to be used independently for gathering flight data. 

## Description

The module will display all flights entering an area, specified as either;

 * A bounding box of latitude and longitude coordinates
 * A rectangular location based on a postal code
 
 Flight data includes;

* Timestamp 
* ICAO24  
* Callsign
* Airline 
* Aircraft 
* Altitude  
* Velocity 
* Track 
* Departure Airport Code, City, and Country
* Destination Airport Code, City, and Country

*Note: not all of the above fields will be available for every flight*

MagicMirror Examples:

![alt text](images/MMM-FlightTracks2.gif)

## Resources

While most of the flight data can be obtained through subscription based APIs, my goal was to implement a solution using open data sources. This led me to the following APIs and repositories; 

* [OpenSky Rest API](https://opensky-network.org/api) for realtime flight tracking data. 
    * MMM-FlightTrack requires the (free) registered version of this API, allowing up to 4000 requests (credits) per day. 

* [OpenSky Aircraft CSV](https://opensky-network.org/datasets/#metadata/) for the aircraft descriptions. 
    * The latest release *(aircraft-database-complete-2025-08.csv)* has been converted to a SQLite database, stored in *data/opensky-aircraft.db*. 
    * The conversion scripts are supplied in the *utils* folder so a new database can be generated when OpenSky releases a new version.  
        * A CSV conversion script *(create_opensky_aircraft_csv.py)* preconditions the supplied aircraft data. 
        * A DB conversion script *(create_opensky_aircraft_db.py)* then converts the processed CSV data into the SQLite database. 

* [Github vradarserver/standing-data](https://github.com/vradarserver/standing-data) for the airline, aircraft, departure & destination route, including the airport code, city, and country. 
    * The latest repository versions have been converted to the following SQLite databases;
        * *data/vradarserver-airline.db* - airline name
        * *data/vradarserver-route.db* - airline routes
        * *data/vradarserver-airport.db* - airport codes IATA, ICAO, location, and country
        * *data/vradarserver-aircraft.db* - aircraft descriptions (prioritized over OpenSky's aircraft data)
    * The corresponding DB conversion scripts are stored in the *utils* folder.

* A preconditioned Airline lookup dictionary also exists within the *airline.py* script. If an airline entry is not found using that dictionary, a secondary lookup will be performed against *vradarserver_airline.db*. 

Note: The entire database build process including all CSV file downloads/pulls, preconditioning, and SQLite operations have been automated within a single bash script *(utils/build.sh)*, which can be invoked via a daily or weekly cron schedule. 


## Installation

In your terminal, go to the MagicMirror's module directory and clone the repository;

```
cd ~/MagicMirror/modules
git clone https://github.com/jdanek24/MMM-FlightTracks.git
```

You will also need to ensure the following Python libraries are installed;

* pip install pandas  
* pip install pgeocode
* pip install python-dotenv


## Configuration

Create an [OpenSky](https://opensky-network.org) account via the *"Sign in, Register"* link, and obtain your ClientID and ClientSecret (token). 

Within the MMM-FlightTrack directory, create an .env file and store those values;

```
#Open-Sky credentials
CLIENT_ID = "foo-api-client"
CLIENT_SECRET = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Next, configure the MMM-FlightTrack module within *config/config.js* file. The following example shows the minimal settings. More options described below.

```
{
    module:"MMM-FlightTracks",
    position:"top_left",
    header: "Flight Tracks",
    config:{
    	postal_code: "08817",		
        country_code: "US",			 
        units: "IMPERIAL",  
    } 
},
```


| Option  | Default | Description | Format |
| ------- | ------- | ----------- | ------ |
| country_code  | "US"  | For postal code lookup and also to omit country name when displaying the airport location | ISO-2 country code |
| units | "IMPERIAL" | Units for aircraft speed *[mph,kph]* and altitude *[ft, m]* | "IMPERIAL" \| "METRIC" |
| lat_min | n/a | Bounding box based coordinates, min latitude, e.g. 40.439 | float | 
| lat_max | n/a | Bounding box based coordinates, max latitude, e.g. 40.5661   | float | 
| lon_min | n/a | Bounding box based coordinates, min longitude, e.g. -74.5219   | float | 
| lon_max | n/a | Bounding box based coordinates, max longitude, e.g. -74.2764   | float | 
| postal_code | n/a | Postal code based coordinates, e.g. "08817". This entry overrides the bounding box entries | str |
| postal_width | 10 |	Postal code width (longitudinal) | int (km) | 
| postal_height | 10 |	Postal code height (latitudinal) | int (km) | 
| max_width | 28 | Truncation length for airline, aircraft, and airport text fields to fit within display location | int|
| no_flight_timer | 60 | Polling wait time when no flights are returned | int (sec) |
| single_flight_timer | 30 | Time to display a single flight. Polling wait time will therefore be 30 seconds| int (sec) |
| multiple_flight_timer | 15 |Time to display each flight when multiple flights are returned. Polling wait time will therefore be 15x seconds where x=2 to the number of returned flights| int (sec) |
| debug | false | Enable Python debug logging | bool |

## Additional Comments

The default polling times have been set to reasonable values that should not exceed OpenSky's daily credit limit. That said, credit usage will vary by the bounding box size. This is documented in OpenSKy's [Limitations](https://openskynetwork.github.io/opensky-api/rest.html#limitations) page. 

The route details for some flights occasionally contain more than two airports, i.e. LGA - JAX - MIA - LGA. To conserve screen space, these routes have been condensed to the first and last unique values, e.g. "LGA - MIA"

Airport codes can be specified in two formats; The 4 letter "ICAO" format used by pilots and air traffic controllers, and the 3 letter "IATA" format more widely recognized by airlines and passengers. This module will default to the IATA value when available, e.g. For Heathrow airport we display "LHR" rather than "EGLL". 

When displaying a route's airport location, the country name will be omitted if it matches config.country_code.  

Active flights are indicated by a flashing "clock" symbol along with a flight count, e.g. (1 of 3). If there are no active flights, the last flight will be displayed in a dimmed font.  

![alt text](images/MMM-FlightTracks1.gif)

## Python usage

The Python flight_tracks.py script adheres to the NodeJS *child_process.spawn* method whereby the request data is supplied as a command line argument and the response data is written to stdout. 

The request data is a json structure based on a subset of the values defined in the Options table above. 

Examples: 
```
% python3 flight_tracks.py  "{\"debug\":true,\"country_code\": \"CA\",\"units\": \"METRIC\",\"lat_min\": 30.0,\"lon_min\": -81.0,\"lat_max\": 32.0,\"lon_max\": -80.0}"; 

% python3 flight_tracks.py  "{\"debug\":false,\"country_code\": \"US\",\"units\": \"IMPERIAL\",\"postal_code\": \"32259\", \"postal_width\": 50, \"postal_height\": 30}"; 
```

Returned flight data is output to stdout as a json array;

```
[stdout]
[
    {
        "timestamp": "10:45 PM",
        "icao24": "a2c92b",
        "callsign": "AAY1330",
        "airline": "Allegiant Air",
        "aircraft": "Airbus A320-214",
        "altitude": "27,750",
        "velocity": "498",
        "track": "N",
        "route": ["SFB", "Orlando", "HGR", "Hagerstown"]
    },
    {
        "timestamp": "10:45 PM",
        "icao24": "a39a13",
        "callsign": "FFT3025",
        "airline": "Frontier",
        "aircraft": "Airbus A320-251N",
        "altitude": "37,000",
        "velocity": "515",
        "track": "NNW",
        "route": ["MIA", "Miami", "CLE", "Cleveland"
        ]
    }
]

% echo "Status:" $?; 
Status: 0

% cat flight_tracks.log
2026-04-03 22:45:28 INFO     flight_tracks: starting
2026-04-03 22:45:28 INFO     flight_tracks: config:{"debug":true,"country_code": "US","units": "IMPERIAL","postal_code": "32259", "postal_width": 50, "postal_height": 30}
2026-04-03 22:45:29 INFO     flight_tracks: flight count: 2
```

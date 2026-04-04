#!/bin/bash

# Update FlightTracks database files
#   Pull data from Github vradarserver/standing-data and store in sqlite database;
#       vradarserver-airport.db
#       vradarserver-route.db
#       vradarserver-aircraft.db
#       vradarserver-airline.db
#   Download most recent OpenSky aircraft data, process, and store in sqlite database;
#       opensky-aircraft.db

# Function to get vradarserver standing-data data
getVradarserver() {
    if [ -d "$TARGET_DIR/.git" ]; then
        # Directory exists, perform a pull
        echo "Directory '$REPO_DIR' already exists. Pulling latest changes"
        git -C "$TARGET_DIR" pull 
    else
        # Directory does not exist, perform a clone
        echo "Directory '$REPO_DIR' does not exist. Cloning repository"
        git clone "$REPO_URL" "$TARGET_DIR"
    fi
}

# Function to get OpenSky aircraft data
getOpenSky() {
    # does file already exists
    if [[ -e "$DOWNLOAD_FILE" ]]; then
        echo "File '$DOWNLOAD_FILE' already exists, skipping download."
    else
        echo "File '$DOWNLOAD_FILE' not found, starting download"
        mkdir -p "$DOWNLOAD_DIR"
        curl -L -o "$DOWNLOAD_FILE" "$FILE_URL"
        if [ $? -eq 0 ]; then
            echo "Download complete."
        else
            echo "Download failed."
        fi
    fi
}

echo "Getting airport, airline, route, and aircraft data (vradarserver)"
REPO_URL="https://github.com/vradarserver/standing-data"
REPO_DIR=$(basename "$REPO_URL" .git)
TARGET_DIR="../data/vradarserver/standing-data/"
getVradarserver

echo "Building airport database (vradarserver)"
rm -f ../data/vradarserver-airport.db  
python3 create_vradarserver_airport_db.py

echo "Building route database (vradarserver)"
rm -f ../data/vradarserver-route.db     
python3 create_vradarserver_route_db.py

echo "Building aircraft database (vradarserver)"
rm -f ../data/vradarserver-aircraft.db     
python3 create_vradarserver_aircraft_db.py

echo "Building airline database (vradarserver)"
rm -f ../data/vradarserver-airline.db     
python3 create_vradarserver_airline_db.py


echo "Getting aircraft data (OpenSky)"
FILE_URL="https://s3.opensky-network.org/data-samples/metadata/aircraft-database-complete-2025-08.csv"
DOWNLOAD_DIR="../data/opensky"
DOWNLOAD_FILE="../data/opensky/aircraft.csv"
TEMP_FILE="../data/opensky/aircraft-processed.csv"

rm -f $TEMP_FILE
rm -f ../data/opensky-aircraft.db   
getOpenSky

echo "Processing aircraft data (OpenSky)"
# NOTE: There are numerous formatting errors in the OpenSky aircraft data file.
# The following line will be deleted due to a non-terminated string;
#   '386bfc','2024-06-25 12:35:50',0,0,,,'',,,,,,,,"Pro,0,,,'386BFC',,'','',,,,,'3697660',,,,ULAC,0
# The remaining (IndexError) errors will handled by the create_aircraft_csv.py conversion script. 

sed  -i ''  '/386bfc/d' $DOWNLOAD_FILE
python3 create_opensky_aircraft_csv.py > $TEMP_FILE

echo "Building aircraft database (OpenSky)"
python3 create_opensky_aircraft_db.py

echo "Done"

'''This module contains the flight routing application'''
__author__ = "jdanek"

import os
import json
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv
import requests

import airline
import aircraft
import route
import heading
import coordinates

# Global Vars
FLIGHT_TRACK_URL = "https://opensky-network.org/api/states/all"
TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
TOKEN_REFRESH_MARGIN = 30
SCRIPT_DIR = Path(__file__).parent.resolve()
LOGGER_FILE = "flight_tracks.log"


# Init logger
logger = logging.getLogger("flight_tracks")
logging.basicConfig(
    filename=SCRIPT_DIR / LOGGER_FILE,
    filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


class TokenManager:
    '''Token class for OpenSky API'''
    def __init__(self, client_id, client_secret):
        self.token = None
        self.expires_at = None
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self):
        '''Return a valid access token, refreshing automatically if needed'''
        if self.token and self.expires_at and datetime.now() < self.expires_at:
            return self.token
        return self._refresh()

    def _refresh(self):
        '''Fetch a new access token from the OpenSky authentication server'''
        r = requests.post(
            TOKEN_URL,
            timeout=30,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        r.raise_for_status()

        data = r.json()
        self.token = data["access_token"]
        expires_in = data.get("expires_in", 1800)
        self.expires_at = datetime.now() + timedelta(seconds=expires_in - TOKEN_REFRESH_MARGIN)
        return self.token

    def headers(self):
        '''Return request headers with a valid token'''
        return {"Authorization": f"Bearer {self.get_token()}"}

def get_velocity(units, meters_per_second) -> str:
    '''Get flight's velocity in specified units'''
    if units == "IMPERIAL":
        result =  str(round(meters_per_second * 2.2369)) # mph
    else:
        result =  str(round(meters_per_second * 3.6)) # kph
    logger.debug( "get_velocity: units: %s, meters_per_second: %f, result: %s", units, meters_per_second, result)
    return result

def get_altitude(units, meters) -> str:
    '''Get flight's altitude in specified units'''
    if units == "IMPERIAL":
        result =  str(format(round(meters * 3.28084),","))  #feet
    else:
        result =  str(format(round(meters),","))  # meters
        logger.debug( "get_altitude: units: %s, meters: %f, result: %s", units, meters, result)
    return result


def parse_state_vector(config, state: List, formatted_time: str) -> Optional[Dict]:
    '''
    Process OpenSky state vector data
    [0] icao24, [1] callsign, [2] origin_country, [3] time_position,
    [4] last_contact, [5] longitude, [6] latitude, [7] baro_altitude,
    [8] on_ground, [9] velocity, [10] true_track, [11] vertical_rate,
    [12] sensors, [13] geo_altitude, [14] squawk, [15] spi, [16] position_source
    '''

    if not state or len(state) < 17:
        return None

    # Skip flights on the ground
    if state[8]:  # on_ground flag
        return None

    callsign = state[1].strip() if state[1] and state[1] != "00000000" else "n/a"
    icao24 = state[0] if state[0] else "n/a"

    flight_data = {
        "timestamp": formatted_time,
        "icao24": icao24,
        "callsign": callsign,
        "airline": airline.get_airline(callsign),
        "aircraft": aircraft.get_aircraft(icao24),
        "altitude": get_altitude(config["units"], state[7]) if state[7] else "n/a",   
        "velocity": get_velocity(config["units"], state[9]) if state[9] else "n/a",   
        "track": heading.get_compass_heading(state[10]) if state[10] else "n/a",  
        "route": route.get_route(config["country_code"], callsign)
    }
    return flight_data


def get_flights(config, tokens) -> List:
    '''Get bounded flights'''
    if "postal_code" in config:
        logger.debug( "get_flights: using postal_code coordinates" )
        bbox = coordinates.get_postal_coordinates(config["country_code"], config["postal_code"], config["postal_width"], config["postal_height"])
        params = {
            "lamin": bbox['lat_min'],
            "lomin": bbox['lon_min'],
            "lamax": bbox['lat_max'],
            "lomax": bbox['lon_max']
        }
    else:
        logger.debug( "get_flights: using bounding box coordinates" )
        params = {
            "lamin": config["lat_min"],
            "lomin": config["lon_min"],
            "lamax": config["lat_max"],
            "lomax": config["lon_max"]   
        }

    response = requests.get(FLIGHT_TRACK_URL, headers=tokens.headers(), params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data or "states" not in data or data["states"] is None:
        return []

    flights = []
    formatted_time = datetime.now().strftime("%I:%M %p")
    for state in data["states"]:
        flight_info = parse_state_vector(config, state, formatted_time)
        if flight_info:
            flights.append(flight_info)
    return flights


def main():
    '''Main function'''
    logger.info("flight_tracks: starting")

    # Load OpenSky API credentials
    load_dotenv()
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    if client_id is None:
        logger.warning("flight_tracks: CLIENT_ID not found")
        print (json.dumps([]))
        sys.exit(1)

    tokens = TokenManager(client_id, client_secret)
    try:
        # Load flight tracking request payload
        json_string = sys.argv[1]
        logger.info("flight_tracks: config: %s", json_string)
        config = json.loads(json_string)

        # Check for debug logging flag
        if config["debug"]:
            logging.basicConfig(
                filename=SCRIPT_DIR / LOGGER_FILE,
                filemode='a',
                format='%(asctime)s %(levelname)-8s %(message)s',
                level=logging.DEBUG,
                datefmt='%Y-%m-%d %H:%M:%S',
                force=True)

        # Request and process flight data
        results = get_flights(config, tokens)
        flights = json.dumps(results)
        logger.info("flight_tracks: flight count: %s", str(len(results)))
        logger.debug("flight_tracks: flights: %s", flights)
        print (flights)

    except Exception as e:
        logger.error(e, exc_info=True)
        print (json.dumps([]))
        sys.exit(1)

if __name__ == "__main__":
    main()

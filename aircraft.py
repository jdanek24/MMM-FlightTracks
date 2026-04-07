'''This module contains aircraft functions'''
__author__ = "jdanek"

import logging
import sqlite3
from pathlib import Path


# Global Vars
SCRIPT_DIR = Path(__file__).parent.resolve()
DB_OPENSKY_AIRCRAFT= "./data/opensky-aircraft.db"
DB_VRADARSERVER_AIRCRAFT = "./data/vradarserver-aircraft.db"

# Init logger
logger = logging.getLogger("flight_tracks")

def get_aircraft(icao24) -> str:
    '''
    Lookup aircraft based on icao24 value using vradarserver database (vradarserver_aircraft.db)
    If not found, then try opensky database (opensky_aircraft.db)
    '''

    logger.debug("get_aircraft: icao24: %s", icao24)
    desc = "n/a"
    if not icao24 or len(icao24) < 6:
        return desc

    # Connect to DB_VRADARSERVER_AIRCRAFT
    conn = sqlite3.connect(SCRIPT_DIR / DB_VRADARSERVER_AIRCRAFT)
    cursor = conn.cursor()
    cursor.execute("SELECT ManufacturerAndModel FROM aircraft WHERE ICAO = ?", (icao24,))
    row = cursor.fetchone()
    if row:
        desc = row[0]
    conn.close()

    if desc == "n/a":
        # Connect to DB_OPENSKY_AIRCRAFT
        conn = sqlite3.connect(SCRIPT_DIR / DB_OPENSKY_AIRCRAFT)
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM aircraft WHERE icao24 = ?", (icao24,))
        row = cursor.fetchone()

        if row:
            desc = row[0]
        conn.close()

    logger.debug("get_aircraft: desc: %s", desc)
    return desc

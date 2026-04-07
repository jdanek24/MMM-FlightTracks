'''This module contains flight tracking coordinates functions'''
__author__ = "jdanek"

import math
import logging
import pgeocode

# Init logger
logger = logging.getLogger("flight_tracks")

def get_postal_coordinates(country_code, postal_code, postal_width, postal_height) -> dict:
    """
    Convert postal code to a latitude/longitude bounding box
    """
    # Define latitude and longitude coordates centered about a postal code
    nomi = pgeocode.Nominatim(country_code)

    logger.debug("get_postal_coordinates: country_code: %s, postal_code: %s, postal_width: %d, postal_height: %d",
                 country_code, postal_code, postal_width, postal_height)
    location = nomi.query_postal_code(str(postal_code))

    if location is None or math.isnan(location.latitude): # type: ignore
        raise ValueError(f"Invalid or unknown postal code: {postal_code}")

    lat = location.latitude
    lon = location.longitude

    # Latitude: 1 deg ≈ 111 km
    delta_lat = (postal_height / 2) / 111.0

    # Longitude varies by latitude
    delta_lon = (postal_width / 2) / (111.0 * math.cos(math.radians(lat)))  # type: ignore

    box = {
        "lat_min": lat - delta_lat,
        "lat_max": lat + delta_lat,
        "lon_min": lon - delta_lon,
        "lon_max": lon + delta_lon
    }
    logger.debug( "get_postal_coordinates: %.4f, %.4f, %.4f, %.4f",
                 box['lat_min'], box['lon_min'], box['lat_max'], box['lon_max'])
    return box

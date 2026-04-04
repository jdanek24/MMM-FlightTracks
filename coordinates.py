__author__ = "jdanek"

import pgeocode
import math
import logging

# Init logger
logger = logging.getLogger("flight_tracks")

def get_postal_coordinates(country_code, postal_code, postal_width, postal_height) -> dict:
    """
    Convert postal code to a latitude/longitude bounding box
    :param postal_code: str or int
    :param postal_width: longitude range (km)
    :param postal_height: latitude range (km)
    :return: dict with lat/lon coordinates
    """
    # Define latitude and longitude coordates centered about a postal code
    nomi = pgeocode.Nominatim(country_code)

    logger.debug(f"get_postal_coordinates: country_code: %s, postal_code: %s, postal_width: %d, postal_height: %d", country_code, postal_code, postal_width, postal_height)
    location = nomi.query_postal_code(str(postal_code))

    if location is None or math.isnan(location.latitude): # type: ignore
        raise ValueError(f"Invalid or unknown postal code: {postal_code}")

    lat = location.latitude
    lon = location.longitude

    # Earth radius in km
    earth_radius = 6371.0

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
    logger.debug( "get_postal_coordinates: %.4f, %.4f, %.4f, %.4f",  box['lat_min'], box['lon_min'], box['lat_max'], box['lon_max'])
    return box

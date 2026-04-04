__author__ = "jdanek"

import logging

# Init logger
logger = logging.getLogger("flight_tracks")

def get_compass_heading(degrees) -> str:
    # convert heading from degrees to 16 compass points
    logger.debug(f"get_compass_heading: degrees: %s", degrees)
    
    points = 16
    maxPoints = 32
    degrees = (degrees + (360/points/2)) / (360/maxPoints)
    j = int(int( int(degrees  % 8)%8 / (maxPoints/points)) * maxPoints/points)
    degrees = int(degrees / 8) % 4
    cardinal = ['North', 'East', 'South', 'West']
    pointDesc = ['W', 'W by x', 'W-z', 'Z by w', 'Z', 'Z by x', 'X-z', 'X by w']
    
    W = cardinal[degrees]
    X = cardinal[(degrees + 1) % 4]
    w = W.lower()
    x = X.lower()
    if (W == cardinal[0] or W == cardinal[2]) :
        Z = W + x
    else:
        Z = X + w
    z = Z.lower()
    
    result = pointDesc[j].replace('W', W).replace('X', X).replace('w', w).replace('x', x).replace('Z', Z).replace('z', z);
    result = result.replace('North', 'N').replace('East', 'E').replace('South', 'S').replace('West', 'W').replace('north', 'N').replace('east', 'E').replace('south', 'S').replace('west', 'W').replace('by', 'b').replace(' ', '').replace('-', '')
    logger.debug(f"get_compass_heading: result: %s", result)
    
    return result

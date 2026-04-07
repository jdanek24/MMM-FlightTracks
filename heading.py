'''This module contains flight heading functions'''
__author__ = "jdanek"

import logging

# Init logger
logger = logging.getLogger("flight_tracks")

def get_compass_heading(degrees) -> str:
    '''
    Convert heading from degrees to 16 compass points
    '''
    logger.debug("get_compass_heading: degrees: %s", degrees)

    points = 16
    max_points = 32
    degrees = (degrees + (360/points/2)) / (360/max_points)
    j = int(int( int(degrees  % 8)%8 / (max_points/points)) * max_points/points)
    degrees = int(degrees / 8) % 4
    cardinal = ['North', 'East', 'South', 'West']
    point_desc = ['W', 'W by x', 'W-z', 'Z by w', 'Z', 'Z by x', 'X-z', 'X by w']

    big_w = cardinal[degrees]
    big_x = cardinal[(degrees + 1) % 4]
    w = big_w.lower()
    x = big_x.lower()
    if (big_w == cardinal[0] or big_w == cardinal[2]) :
        big_z = big_w + x
    else:
        big_z = big_x + w
    z = big_z.lower()

    result = point_desc[j].replace('W', big_w).replace('X', big_x).replace('w', w).replace('x', x).replace('Z', big_z).replace('z', z)
    result = (result.replace('North', 'N').replace('East', 'E').replace('South', 'S').replace('West', 'W').replace('north', 'N')
        .replace('east', 'E').replace('south', 'S').replace('west', 'W').replace('by', 'b').replace(' ', '').replace('-', ''))
    logger.debug("get_compass_heading: result: %s", result)

    return result

"""
--|__init__.py|--
Part of: UberAnalysis
Author: James Lynch
Created On: 5/13/17
"""

import configparser
from uber_rides.session import Session
from uber_rides.client import UberRidesClient

"""Grab the relevant credentials"""
PARSER = configparser.ConfigParser()
PARSER.read('appinfo.ini')


session = Session(server_token=PARSER['Uber']['server_token'])
CLIENT = UberRidesClient(session)


# ======================================================================================================================
def get_price(service, start, end):
    """
    Using the client object as a request handler, pulls the prices for an Uber POOL trip and
        returns it as a dictionary

    :param UberRidesClient client:  API client to handle data collection.
    :param str service: The string name of the service (which should match 'display_name')
    :param tuple float start: a tuple in the format of (lat, long) representing the start coordinates
    :param tuple float end: a tuple in the format of (lat, long) representing the end coordinates

    :return: a dictionary with the pricing information
    :rtype: dict
    """

    response = CLIENT.get_price_estimates(
        start_latitude=start[0],
        start_longitude=start[1],
        end_latitude=end[0],
        end_longitude=end[1],
        seat_count=1
    )

    # Construct a dictionary before the loop. If we hit the 'POOL' entry in the estimates,
    # populate it and then return it. Otherwise, the function returns a NoneType

    output = {}

    # If there's more than one POOL estimate, this will break...but I can't fathom that happening

    estimates = response.json.get('prices')
    for estimate in estimates:
        if estimate['display_name'] == service:
            output['low_estimate'] = estimate['low_estimate']
            output['high_estimate'] = estimate['high_estimate']
            output['duration'] = estimate['duration']

            return output


# ----------------------------------------------------------------------------------------------------------------------
def get_all(service, start, coordinates):
    """
    Returns a list of dictionary outputs similar to the output of get_price, only with the added
        key 'destination'

    :param UberRidesClient client: API client object to handle data collection
    :param str service: String value representing the service we want to search (i.e., uberX)
    :param tuple floar start: starting coordinates
    :param list dict coordinates: A list of dicts in the format dest: (lat, long)
    :return: a list of dictionaries
    :rtype: list of dict
    """

    output = []
    for dest, coord in coordinates.items():
        price_info = get_price(service, start, coord)
        price_info['destination'] = dest
        output.append(price_info)
    return output


def read_destinations(parser):
    """
    Uses the provided ConfigParser object to read the destination values into a dictionary
        usable by the major functions in this module
    :param configparser.ConfigParser parser: parser with a .ini file loaded
                                                (this file must have a [Destinations] section)
    :return: A dictionary of the format {"destination name": (float lat, float long)}
    :rtype: dict
    """

    output = dict()

    # Remember, we are assuming the ConfigParser has already loaded the .ini
    for dest, coord_string in parser['Destinations'].items():
        # Figure out where the delimiter is
        delim_i = coord_string.index(',')
        output[dest] = (float(coord_string[:delim_i]), float(coord_string[delim_i + 1:]))

    return output


# ======================================================================================================================

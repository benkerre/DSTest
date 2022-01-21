import sys
sys.path.insert(0, './src')
import urllib
import datetime
import asyncio
import aiohttp
import pandas as pd
import urllib.request
from io import BytesIO
from dateutil.parser import parse as parse_time

"""
    We are trying to build the target url from the parameters passed to the get_earthquake_data(**kwargs) function
    url will be of the form:: https://earthquake.usgs.gov/fdsnws/event/1/[METHOD[?PARAMETERS]]
    METHOD := query [to submit a data request]
    PARAMETERS := ?
"""

######################
# USGS API parameters
######################

METHOD_PARAM = METHOD_ARG = "query"
FORMAT_PARAM = FORMAT_ARG = 'format'
START_DATE_PARAM = START_DATE_ARG = 'starttime'
END_DATE_PARAM = END_DATE_ARG= 'endtime'
LATITUDE_PARAM = LATITUDE_ARG = 'latitude'
LONGITUDE_PARAM = LONGITUDE_ARG = 'longitude'
MAX_RADIUS_KM_PARAM = MAX_RADIUS_KM_ARG = 'maxradiuskm'
MIN_MAGNITUDE_PARAM = MIN_MAGNITUDE_ARG = 'minmagnitude'
EVENT_PARAM = EVENT_ARG = 'eventtype'
DISTANCE_COLUMN = 'distance'

############
# Functions
############

def parse_arg(arguments):
    """
        This function parses the arguments of the get_earthquake_data function to build the parameters of
        the request to send in HTTP.
        :param arguments the arguments passed to the "get_earthquake_data" function (ex: latitude, longitude, radius ...)
    """

    if not arguments:
        raise ValueError("No arguments were provided.")

    parameters = {}    
    parameters[METHOD_PARAM] = "query" # We choose "query" as method
    parameters[FORMAT_PARAM] = 'csv'   # "csv" as format
    parameters[EVENT_PARAM] = arguments[EVENT_ARG] if (EVENT_ARG in arguments) else "earthquake"  # "earthquake" as eventtype to filter no earthquake event
    
    if START_DATE_ARG in arguments:
        if not isinstance(arguments[START_DATE_ARG], datetime.date):
            try:
                parameters[START_DATE_PARAM] = parse_time(arguments[START_DATE_ARG])
            except:
                raise ValueError("START_DATE_ARG does not have the correct format.")

        else:
            parameters[START_DATE_PARAM] = arguments[START_DATE_ARG]
    
    if END_DATE_ARG in arguments:
        if not isinstance(arguments[END_DATE_ARG], datetime.date):
            try:
                parameters[END_DATE_PARAM] = parse_time(arguments[END_DATE_ARG])
            except:
                raise ValueError("END_DATE_ARG does not have the correct format.")
        else:
            parameters[END_DATE_PARAM] = arguments[END_DATE_ARG]

    if LATITUDE_ARG in arguments:
        if not isinstance(arguments[LATITUDE_ARG], (int, float)):
            raise ValueError("LATITUDE_ARG must be numeric.")
        parameters[LATITUDE_PARAM] = arguments[LATITUDE_ARG]
    
    if LONGITUDE_ARG in arguments:
        if not isinstance(arguments[LONGITUDE_ARG], (int, float)):
            raise ValueError("LONGITUDE_ARG must be numeric .")
        parameters[LONGITUDE_PARAM] = arguments[LONGITUDE_ARG]
    
    if MAX_RADIUS_KM_ARG in arguments:
        if not isinstance(arguments[MAX_RADIUS_KM_ARG], (int, float)) or arguments[MAX_RADIUS_KM_ARG] <= 0:
            raise ValueError("MAX_RADIUS_KM_ARG must be numeric and >0.")
        parameters[MAX_RADIUS_KM_PARAM] = arguments[MAX_RADIUS_KM_ARG]

    if MIN_MAGNITUDE_ARG in arguments:
        if not isinstance(arguments[MIN_MAGNITUDE_ARG], (int, float)) or arguments[MIN_MAGNITUDE_ARG]<0 :
            raise ValueError("MIN_MAGNITUDE_PARAM must be numeric and >=0.")
        parameters[MIN_MAGNITUDE_PARAM] = arguments[MIN_MAGNITUDE_PARAM]
    
    return parameters


def build_api_url(parameters):
    """
        This function  create the requested api url using:
            :param parameters: parametrers returned by parse_arg function
            :return: the target_url := https://earthquake.usgs.gov/fdsnws/event/1/query?[PARAMETERS]
            :example:= https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2014-01-01&endtime=2014-01-02&eventtype="earthquake"
    """
    if LATITUDE_PARAM not in parameters or LONGITUDE_PARAM not in parameters or MIN_MAGNITUDE_PARAM not in parameters:
        raise ValueError('LATITUDE_PARAM, LONGITUDE_PARAM and MIN_MAGNITUDE_PARAM must be provided..')
    method = parameters.pop(METHOD_PARAM)
    parse_params = urllib.parse.urlencode(parameters)
    requested_url = 'https://earthquake.usgs.gov/fdsnws/event/1/{}?'.format(method) + parse_params
    return requested_url


def get_earthquake_data(**kwargs):
    """
       The function will retrieve the earthquake data of the area of interest for the past 200 years
       :param START_DATE: Limit to events on or after the specified start time. 
       :param END_DATE: Limit to events on or before the specified end time.
       :param LATITUDE: Specify the latitude to be used for a radius search.
       :param LONGITUDE: Specify the longitude to be used for a radius search.
       :param MAX_RADIUS_KM: Limit to events within the specified maximum number of kilometers from the geographic point defined by the latitude and longitude parameters. 
       :param MIN_MAGNITUDE: Limit to events with a magnitude larger than the specified minimum.
    """
    parameters = parse_arg(kwargs)
    # Reset START_DATE_ARG
    if END_DATE_PARAM in parameters:
        parameters[START_DATE_PARAM] = parameters[END_DATE_PARAM] - pd.DateOffset(years=200)
    requested_url = build_api_url(parameters)
    response = urllib.request.urlopen(requested_url)
    data = pd.read_csv(BytesIO(response.read())) if response.status==200 else None
    return data


# *****************
# *****************
# ****  Async  ****
# *****************
# *****************

async def async_get_earthquake_data(session, target_url):
    data = None
    async with session.get(target_url) as response:
        if response.status == 200:
            data = await response.read()
            data = pd.read_csv(BytesIO(data))
        return data

async def get_earthquake_data_for_multiple_locations(assets, **kwargs):
    # Reset START_DATE_ARG
    if END_DATE_PARAM in kwargs:
            kwargs[START_DATE_ARG] = kwargs[END_DATE_ARG] - pd.DateOffset(years=200)
    async with aiohttp.ClientSession() as session:
        coroutines = []
        for asset in assets:
            # Parse arg 
            parameters = parse_arg(kwargs)
            # Get LATITUDE_PARAM and LONGITUDE_PARAM parameters
            parameters[LATITUDE_PARAM], parameters[LONGITUDE_PARAM] = asset
            # Build aoi url
            target_url = build_api_url(parameters)
            # In order to get multiple coroutines running on the event loop, we're using
            # asyncio.ensure_future() and then run the loop forever to process everything.
            task = asyncio.ensure_future(async_get_earthquake_data(session=session,target_url=target_url))
            coroutines.append(task)
        # Collect responses
        responses = await asyncio.gather(*coroutines)
        data = pd.concat(responses, ignore_index=True)
        data.drop_duplicates(inplace=True)
    return data
    
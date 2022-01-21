import pandas as pd
from math import cos, sin, sqrt, asin, pi

################
# Com
################

def compute_single(p1, p2):
    """
        This function compute the haversine distance between two points.
        :p1 (lat1, lon1)
        :p2 (lat2, lon2)
        :retun the distance between p1 and p2
    """
    lat1, lon1 = p1
    lat2, lon2 = p2
    # convert to radians
    lat1 = (lat1) * pi / 180.0
    lat2 = (lat2) * pi / 180.0
    # Diff longitudes/latitudes
    dLat = (lat2 - lat1) * pi / 180.0
    dLon = (lon2 - lon1) * pi / 180.0
    # apply formulae
    area = sin(dLat/2)**2 + sin(dLon/2)**2 *  cos(lat1) * cos(lat2)
    radius = 6378.0
    distance = 2 * asin(sqrt(area)) * radius
    return abs(distance)

def get_haversine_distance(earthquakeDataLatitudes,  earthquakeDataLongitudes, clientLatitude, clientLongitude):
    """
        Calculate the haversine distance between the client and all points in the area of interest.
    """
    size = len(earthquakeDataLatitudes)
    distances = map(compute_single, zip(earthquakeDataLatitudes, earthquakeDataLongitudes), ((clientLatitude, clientLongitude) for _ in range(size)))
    return list(distances)

def compute_payouts(earthquake_data, payout_structure):
    assert earthquake_data is not None, 'earthquake==None!'
    earthquake_data_copy = earthquake_data.copy()
    payouts = {}
    # Reset earthquake data index to time index
    earthquake_data_copy['time'] = pd.to_datetime(earthquake_data_copy['time'])
    earthquake_data_copy.index = earthquake_data_copy['time']
    earthquake_data_copy = earthquake_data_copy.drop('time', axis=1)
    # Resample earthquake data by year
    resampled_earthquake_data = earthquake_data_copy.resample('Y')
    # Get years 
    indices = resampled_earthquake_data.indices
    for year in indices:
        # Get data[year]
        year_group = resampled_earthquake_data.get_group(year)
        payouts[year.year] = 0
        for payout in payout_structure:
            # if all 'mag' > mag_payout and dis <= dis_payout
            if any((year_group['distance'] <= payout[0]) & (year_group['mag'] >= payout[1])):
                # Update payouts[year] to the maximum 
                payouts[year.year] = payout[2] if payouts[year.year] < payout[2] else payouts[year.year]
    return payouts


def compute_burning_cost(payouts, start_year, end_year):
    assert end_year >= start_year, "endyear < startyear"
    sum_payouts = 0
    # Time range.
    nb_years = end_year-start_year+1
    for year in range(start_year, end_year+1):
        if year in payouts:
        # If year in time range add the payouts[year]
            sum_payouts += payouts[year]
    return sum_payouts/nb_years



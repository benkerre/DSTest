import sys
sys.path.insert(0, './')

import unittest
from src.earthquakes.usgs_api import build_api_url, parse_arg


class TestParseArg(unittest.TestCase):

    def test_LATITUDE_ARG_is_numeric(self):
        arguments = {'latitude':'38.03'}
        with self.assertRaises(ValueError):
            parse_arg(arguments)

    def test_LONGITUDE_ARG_is_numeric(self):
        arguments = {'longitude':'38.03'}
        with self.assertRaises(ValueError):
            parse_arg(arguments)

    def test_MIN_MAGNITUDE_ARG_is_numeric(self):
        arguments = {'minmagnitude':'4.5'}
        with self.assertRaises(ValueError):
            parse_arg(arguments)

    def test_MIN_MAGNITUDE_ARG_is_negative(self):
        arguments = {'minmagnitude':-10}
        with self.assertRaises(ValueError):
            parse_arg(arguments)

    def test_MAX_RADIUS_KM_ARG_is_numeric(self):
        arguments = {'maxradiuskm':'200'}
        with self.assertRaises(ValueError):
            parse_arg(arguments)

    def test_MAX_RADIUS_KM_ARG_is_negative(self):
        arguments = {'maxradiuskm':-10}
        with self.assertRaises(ValueError):
            parse_arg(arguments)

    def test_START_DATE_ARG_correct_format(self):
        arguments = {'starttime':'2021.10$02'}
        with self.assertRaises(ValueError):
            parse_arg(arguments)

    def test_START_END_ARG_correct_format(self):
        arguments = {'endtime':'2021.10$02'}
        with self.assertRaises(ValueError):
            parse_arg(arguments)

class TestBuildApiUrl(unittest.TestCase):

    def test_LATITUDE_ARG_in_parameters(self):
        parameters = {'longitude':38.03, 'starttime':'2000-01-01', 'minmagnitude':5, 'endtime':'2022-01-01'}
        with self.assertRaises(ValueError):
            build_api_url(parameters)
    
    def test_LONGITUDE_ARG_in_parameters(self):
        parameters = {'latitude':38.03, 'starttime':'2000-01-01', 'minmagnitude':5, 'endtime':'2022-01-01'}
        with self.assertRaises(ValueError):
            build_api_url(parameters)

    def test_MIN_MAGNITUDE_ARG_in_parameters(self):
        parameters = {'latitude':32.19, 'longitude':38.03, 'starttime':'2000-01-01', 'endtime':'2022-01-01'}
        with self.assertRaises(ValueError):
            build_api_url(parameters)
    
    def test_LATITUDE_ARG_LONGITUDE_ARG_MIN_MAGNITUDE_ARG_in_parameters(self):
        parameters = {'starttime':'2000-01-01', 'endtime':'2022-01-01'}
        with self.assertRaises(ValueError):
            build_api_url(parameters)

if __name__ == '__main__':
    unittest.main()
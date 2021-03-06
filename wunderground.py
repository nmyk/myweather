from __future__ import print_function
import json
import logging
import urllib
from os import environ
from urllib2 import urlopen, URLError
from time import sleep

logging.basicConfig()
log = logging.getLogger(__name__)

_BASE_URL = \
        'http://api.wunderground.com/api/{key}/hourly10day{location_url}.json'


def _parse_json(json_data):
    ''' Parse json returned from wunderground API into list of dicts with
        only the data we care about.
    '''
    if 'hourly_forecast' not in json_data or not json_data['hourly_forecast']:
        logging.error('json data is ill-formed')
        return []

    def get_dict(row):
        return dict(
            date=int(row['FCTTIME']['epoch'])*1000,
            icon=row['icon_url'],
            icon_pos=100,
            pop=row['pop'],                    # probability of precipitation
            temp=row['temp']['english'],       # temperature in Fahrenheit
            temp_c=row['temp']['metric'],      # Celsius
            feel=row['feelslike']['english'],  # temperature it feels like
            feel_c=row['feelslike']['metric'])
    return [get_dict(row) for row in json_data['hourly_forecast']]


def autocomplete_user_input(user_input):
    ''' Takes contents of 'enter zip code or city' field and gives it to the
    wunderground autocomplete API. Returns the url and name of the top
    result, e.g.

    '/q/zmw:10027.1.99999', '10027 - New York, NY',
    '''
    url = ('http://autocomplete.wunderground.com/aq?query=%s'
           % urllib.quote(user_input.encode('utf-8')))
    response = json.load(urlopen(url))
    # will raise an IndexError if RESULTS is empty
    top_result = response['RESULTS'][0]
    return top_result['l'], top_result['name']


def _json_for_url(location_url, api_key):
    if api_key == 'development':
        logging.error('You need to set WUNDERGROUND_KEY in your environment')
        return {}
    url = _BASE_URL.format(key=api_key, location_url=location_url)
    for i in range(3):
        try:
            return json.load(urlopen(url))
        except URLError:
            sleep(i)
    raise URLError('urlopen timeout max retries')


def weather_for_url(url, api_key):
    return _parse_json(_json_for_url(url, api_key))


def jsonify(weather_data):
    row_string = ("{{date: new Date({date}), icon: '{icon}', "
                  "icon_pos: {icon_pos}, temp: {temp}, pop: {pop}, "
                  "feel: {feel}, temp_c: {temp_c}, feel_c: {feel_c}}}")
    stringified = [row_string.format(**row) for row in weather_data]
    return "[" + ",\n".join(stringified) + "]"

if __name__ == "__main__":
    url = '/q/zmw:10027.1.99999'
    try:
        api_key = environ['WUNDERGROUND_KEY']
    except KeyError:
        print('enter weather underground api key:')
        api_key = raw_input()
    json_data = _json_for_url(url, api_key)
    weather_data = _parse_json(json_data)[:12]
    for row in weather_data:
        print(row)
    json_string = jsonify(weather_data)
    print(json_string)

import os
import googlemaps
from templates import answer
from managers import CsvReader
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from googlemaps.elevation import elevation

geolocator = Nominatim()
gmaps = googlemaps.Client(key='') # TODO


def capital_loc(capital):
    if capital:
        for country in csv_reader():
            if country['capital'] == capital:
                return (country['latitude'], country['longitude'])


def csv_reader(path='countries.csv'):
    with CsvReader(path) as csv_object:
        for line in csv_object:
            yield line


def get_city(data):
    for key in ['city', 'town', 'village']:
        if key in data:
            return data[key]


def car_time(capital, lat, long):
    if capital:
        direction = gmaps.directions(mode='driving', origin=(lat, long), destination=capital)
        try:
            return direction[0]['legs'][0]['duration']['text']
        except IndexError: pass
    return 'not found'


def direct_distance(capital, lat, long):
    if capital:
        return round(geodesic((lat, long), capital).km)
    return 'not found'


def collect(data, lat, long):
    country_code = data['address']['country_code']
    capital = get_capital(country_code)
    capital_location = capital_loc(capital)
    city = get_city(data['address'])
    return {
        'verbose_name': data['display_name'],
        'country': data['address']['country'],
        'city': city or 'not found',
        'capital': capital,
        'elevation': round(elevation(gmaps, (float(lat), float(long)))[0]['elevation']),
        'street': data['address'].get('road', 'not found'),
        'state': data['address'].get('state', 'not found'),
        'postcode': data['address'].get('postcode', 'not found'),
        'house': data['address'].get('house_number', 'not found'),
        'code': country_code,
        'direct': direct_distance(capital_location, lat, long),
        'car_time': car_time(capital_location, lat, long)
    }


def by_address(address):
    location = geolocator.geocode(address, language='en', timeout=1000)
    if location:
        return by_coordinates(location.raw['lat'], location.raw['lon'])
    return 'Not found'


def get_capital(code):
    for country in csv_reader():
        if country['code'].lower() == code:
            return country['capital']


def by_coordinates(lat, long):
    location = geolocator.reverse(f"{lat}, {long}", language='en', timeout=1000)
    if location and location.raw.get('address'):
        return answer.format(**collect(location.raw, lat, long))
    return 'Not found'


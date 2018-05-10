import os
import googlemaps
from nearly import haversine
from templates import answer
from managers import CsvReader
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from googlemaps.elevation import elevation
from collections import namedtuple, defaultdict

geolocator = Nominatim()
gmaps = googlemaps.Client(key=os.environ.get('google_key'))
capital_dist = namedtuple('Distance', ['name', 'distance'])


def nearly_capitals(lat, long):
    distances = []
    for i in csv_reader():
        c_lat, c_long = float(i['latitude']), float(i['longitude'])
        distance = haversine(*map(float, (lat, long)), c_lat, c_long)
        if distance != 0:
            distances.append(capital_dist(i['capital'], distance))
    return sorted(distances, key=lambda x: x.distance)[:3]


def capital_loc(capital):
    if capital:
        for country in csv_reader():
            if country['capital'] == capital:
                return (country['latitude'], country['longitude'])


def csv_reader(path='source/countries.csv'):
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


def collect(display, data, lat, long):
    country_code = data['country_code']
    capital = get_capital(country_code)
    capital_location = capital_loc(capital)
    city = get_city(data)
    return {
        'verbose_name': display,
        'country': data['country'],
        'city': city or 'not found',
        'capital': capital,
        'elevation': round(elevation(gmaps, (float(lat), float(long)))[0]['elevation']),
        'street': data['road'],
        'state': data['state'],
        'postcode': data['postcode'],
        'house': data['house_number'],
        'code': country_code,
        'direct': direct_distance(capital_location, lat, long),
        'car_time': car_time(capital_location, lat, long),
        'near': ', '.join([x.name for x in nearly_capitals(lat, long)])
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
        display = location.raw['display_name']
        data = defaultdict(lambda: 'not found', location.raw['address'])
        return answer.format(**collect(display, data, lat, long))
    return 'Not found'

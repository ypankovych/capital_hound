import csv
from countryinfo import countries
from collections import namedtuple
from geopy.geocoders import Nominatim

geolocator = Nominatim()
fields = ['code', 'capital', 'latitude', 'longitude']
coordinates = namedtuple('Coordinates', ['latitude', 'longitude'])


def by_address(address):
    location = geolocator.geocode(address, language='en', timeout=1000)
    if location:
        return coordinates(location.raw['lat'], location.raw['lon'])


def shaping(data):
    rows = []
    for i in data:
        coordinates = by_address(i['capital'])
        if coordinates:
            rows.append({'code': i['code'], 'capital': i['capital'], **coordinates._asdict()})
    return rows


def csv_writer(path, fieldnames, data):
    with open(path, "w", newline='', encoding='utf8') as out_file:
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


if __name__ == '__main__':
    csv_writer('countries.csv', fields, shaping(countries))

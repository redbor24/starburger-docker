import requests
from django.conf import settings
from geopy import distance
from location.models import Location


def fetch_coordinates(address):
    response = requests.get(settings.GEO_ENGINE_BASE_URL, params={
        'geocode': address,
        'apikey': settings.YANDEX_GEOCODER_API,
        'format': 'json',
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(' ')
    return lat, lon


def get_distance(order, locations):
    order_coordinates = locations.get(order.delivery_address)
    order.order_has_no_coords = not any(order_coordinates)
    if not order.order_has_no_coords:
        for restaurant in order.restaurants:
            restaurant_coordinates = locations.get(restaurant.address)
            restaurant.distance_for_order = round(distance.distance(order_coordinates, restaurant_coordinates).km, 3)
    return order


def get_locations(*addresses):
    locations = {
        location.address: (location.lat, location.lon)
        for location in Location.objects.filter(address__in=addresses)
    }
    new_locations = list()
    for address in addresses:
        if address in locations.keys():
            continue
        coordinates = fetch_coordinates(address)
        if coordinates:
            lat, lon = coordinates
        else:
            lat, lon = None, None
        location = Location(address=address, lat=lat, lon=lon)
        locations[location.address] = (location.lat, location.lon,)
        new_locations.append(location)
    Location.objects.bulk_create(new_locations)
    return locations

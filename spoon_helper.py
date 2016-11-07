import json
import os
import urllib

import requests


class SpoonHelper(object):
    crontable = []

    outputs = []
    ACCESS_TOKEN = os.environ['GOOGLE_TOKEN']

    def build_search_url(self, search_text='', type_text=''):
        base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'  # Can change json to xml to change output type
        key_string = '?key=' + self.ACCESS_TOKEN  # First think after the base_url starts with ? instead of &
        query_string = ''
        if search_text != '':
            query_string = '&keyword=' + urllib.quote(search_text)
        distance_string = '&location=49.285174,-123.1261515&rankby=distance'
        type_string = ''
        if type_text != '':
            type_string = '&type=' + urllib.quote(type_text)  # More on types: https://developers.google.com/places/documentation/supported_types
        url = base_url + key_string + query_string + type_string + distance_string
        return url

    def build_details_url(self, placeid):
        base_url = 'https://maps.googleapis.com/maps/api/place/details/json'  # Can change json to xml to change output type
        key_string = '?key=' + self.ACCESS_TOKEN  # First think after the base_url starts with ? instead of &
        placeid_string = '&placeid=' + placeid
        url = base_url + key_string + placeid_string
        return url

    def pretty_print(self, result):
        details_result = json.loads(requests.get(self.build_details_url(result['place_id'])).content)
        details = details_result['result']
        name = '*' + result['name'] + '*'
        address = '\n' + details['formatted_address']
        price = ''
        if 'price_level' in details:
            price = '\nPrice: ' + PriceRating(details['price_level'])
        rating = ''
        if 'rating' in details:
            rating = '\nRating: ' + str(details['rating'])
        phone_number = ''
        if 'international_phone_number' in details:
            phone_number = '\nPhone: ' + details['international_phone_number']
        website = ''
        if 'website' in details:
            website = '\nWebsite: ' + details['website']
        google_maps_url = ''
        if 'url' in details:
            google_maps_url = '\nGoogle Maps: ' + details['url']
        pretty_result = name + address + price + rating + phone_number + website + google_maps_url
        return pretty_result


class PriceRating:
    def __init__(self, price_level):
        self.price_level = price_level

    def __str__(self):
        return {
            0: 'Free',
            1: 'Inexpensive',
            2: 'Moderate',
            3: 'Expensive',
            4: 'Very Expensive'
        }.get(self.price_level, 'Pricing unavailable')

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)

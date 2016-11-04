import os
import urllib
import requests
import re
import json

crontable = []
outputs = []
ACCESS_TOKEN = os.environ['GOOGLE_TOKEN']


def process_message(data):
    match = re.search(r"(^|\W)eat\W*([\w &+'.]+)?", data['text'])
    if match is not None:
        url = build_search_url(match.group(2), 'restaurant')
        response = requests.get(url)
        jsoncontent = json.loads(response.content)
        results = jsoncontent['results']
        results = [result for result in results if 'permanently_closed' not in result]
        num_results = len(results)
        if num_results < 5:
            outputs.append([data['channel'], '{} result(s) found:'.format(num_results)])
        elif 'next_page_token' in jsoncontent:
            outputs.append([data['channel'], 'More than 5 results found:'])
        else:
            outputs.append([data['channel'], '5 results found:'])

        for result in results[:5]:
            outputs.append([data['channel'], pretty_print(result)])


def build_search_url(search_text='', type_text=''):
    base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'  # Can change json to xml to change output type
    key_string = '?key=' + ACCESS_TOKEN  # First think after the base_url starts with ? instead of &
    query_string = ''
    if search_text != '':
        query_string = '&keyword=' + urllib.quote(search_text)
    distance_string = '&location=49.285174,-123.1261515&rankby=distance'
    type_string = ''
    if type_text != '':
        type_string = '&type=' + urllib.quote(type_text)  # More on types: https://developers.google.com/places/documentation/supported_types
    url = base_url + key_string + query_string + type_string + distance_string
    return url


def build_details_url(placeid):
    base_url = 'https://maps.googleapis.com/maps/api/place/details/json'  # Can change json to xml to change output type
    key_string = '?key=' + ACCESS_TOKEN  # First think after the base_url starts with ? instead of &
    placeid_string = '&placeid=' + placeid
    url = base_url + key_string + placeid_string
    return url


def pretty_print(result):
    details_result = json.loads(requests.get(build_details_url(result['place_id'])).content)
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

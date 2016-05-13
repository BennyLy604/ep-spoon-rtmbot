import os
import urllib
import requests
import re
import json

crontable = []
outputs = []
ACCESS_TOKEN = os.environ['GOOGLE_TOKEN']


def process_message(data):
    match = re.search(r"(^|\W)eat\W*([\w ']+)?", data['text'])
    if match is not None:
        url = build_search_url(match.group(2), 'restaurant')
        response = requests.get(url)
        jsoncontent = json.loads(response.content)
        results = jsoncontent['results']
        num_results = len(results)
        if num_results < 20:
            outputs.append([data['channel'], '{} results found:'.format(num_results)])
        elif jsoncontent['next_page_token']:
            outputs.append([data['channel'], 'More than 20 results found:'])
        else:
            outputs.append([data['channel'], '20 results found:'])

        for result in results:
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
    address = '\n' + details_result['result']['formatted_address']
    pretty_result = result['name'] + address
    return pretty_result

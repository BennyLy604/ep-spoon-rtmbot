import json
import re

import requests

from spoon_helper import SpoonHelper

outputs = []


def process_message(data):
    match = re.search(r"(^|\W)eat\W*([\w &+'.]+)?", data['text'])
    if match is not None:
        spoon_helper = SpoonHelper()
        url = spoon_helper.build_search_url(match.group(2), 'restaurant')
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
            outputs.append([data['channel'], spoon_helper.pretty_print(result)])

from __future__ import print_function
import json
import os

import requests
from flask import Flask, request, Response, g

from spoon_helper import SpoonHelper

app = Flask(__name__)

SLACK_WEBHOOK_SECRET = os.environ['SLACK_WEBHOOK_SECRET']


@app.route('/slack', methods=['POST'])
def inbound():
    if request.form.get('token') == SLACK_WEBHOOK_SECRET:
        channel = request.form.get('channel_name')
        username = request.form.get('user_name')
        text = request.form.get('text')
        inbound_message = username + " in " + channel + " says: " + text
        print(inbound_message)

        @multi_message_response
        def send_five_results(resp):
            response_url = request.form.get('response_url')

            spoon_helper = SpoonHelper()
            url = spoon_helper.build_search_url(text, 'restaurant')
            response = requests.get(url)
            jsoncontent = json.loads(response.content)
            results = jsoncontent['results']
            results = [result for result in results if 'permanently_closed' not in result]

            info_string = username + " has searched for \"" + text + "\".\n" + str(len(results)) + " result(s) found.\n"

            if len(results) == 0:
                return Response(info_string)
            else:
                for index, result in enumerate(results[:5]):
                    result_string = spoon_helper.pretty_print(result)
                    if index == 0:
                        result_string = info_string + result_string
                    res_response = requests.post(response_url,
                                                 json={"response_type": "in_channel",
                                                       "text": result_string})
                    print(res_response.status_code)
                    print(response_url)

            return resp

    print("returning response")
    return Response(), 200


@app.route('/', methods=['GET'])
def test():
    return Response('It works!')


def multi_message_response(func):
    if not hasattr(g, 'call_after_request'):
        g.call_after_request = []
    g.call_after_request.append(func)
    return func


@app.after_request
def per_request_callbacks(response):
    for func in getattr(g, 'call_after_request', ()):
        response = func(response)
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, debug=1, host="0.0.0.0")

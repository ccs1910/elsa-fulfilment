# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


'''
@author : csantoso
@references : 
translator : https://github.com/dialogflow/fulfillment-webhook-translate-python/blob/master/APP.py
weather : https://github.com/dialogflow/fulfillment-webhook-weather-python
'''

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import random

from flask import Flask, jsonify, make_response, request

import google_translator
import yahoo_weather_api


# Flask APP should start in global layout
APP = Flask(__name__)
LOG = APP.logger

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    
    action = req.get("result").get("action")
    
    if action == "yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = yahoo_weather_api.makeYqlQuery(req)
        if yql_query is None:
            return {}
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
        result = urlopen(yql_url).read()
        data = json.loads(result)
        res = yahoo_weather_api.makeYahooWeatherResult(data)
        
    elif action == "digitalmomtakingnotes":
        baseurl = "https://aaa7512d.ngrok.io/taking_notes"
        content = urlopen(baseurl).read()
        res = makeDigitalMoMResult()
        
    elif action == "translate.text" :
        # Get the parameters for the translation
        text = req['result']['parameters'].get('text')
        source_lang = req['result']['parameters'].get('lang-from')
        target_lang = req['result']['parameters'].get('lang-to')

        # Fulfill the translation and get a response
        output = google_translator.translate(text, source_lang, target_lang)

        # Compose the response to API.AI
        res = {'speech': output,
               'displayText': output,
               'contextOut': req['result']['contexts']}
    else:
        # If the request is not to the translate.text action throw an error
        LOG.error('Unexpected action requested: %s', json.dumps(req))
        res = {'speech': 'error', 'displayText': 'error'}
        
    return res


    
def makeDigitalMoMResult(data):
    
    # print(json.dumps(item, indent=4))

    speech = "Let's start take notes"

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "elsa-digitalMoM"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting APP on port %d" % port)

    APP.run(debug=False, port=port, host='0.0.0.0')

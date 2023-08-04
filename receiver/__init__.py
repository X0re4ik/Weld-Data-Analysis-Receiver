from flask import Flask, request
from receiver.rw_device_manager import rw_device_manager


import logging


app = Flask(__name__)

import json
import time

@app.route('/write_values', methods=["POST"])
def write_values():
    #request.authorization["username"]
    data = json.loads(request.get_json())
    ID = data["ID"]
    measurements = data["measurements"]
    now = time.time()
    for measurement in measurements:
        measurement.update({"ID": ID})
        rw_device_manager.add(measurement)
    end = time.time()
    return {
        "success": True,
        "period": end - now
    }

from flask import Response
@app.route('/test_write_values', methods=["POST"])
def test_write_values():
    print(request.is_json)
    print(request.get_json())
    
    answer = json.dumps({
        'state': 'ON'
    })
    return Response(answer, status=200)




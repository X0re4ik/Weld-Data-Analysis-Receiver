import json

from flask import Flask, request, Response
from werkzeug.datastructures import Headers
from datetime import datetime

from receiver.rw_device_manager import rw_device_manager

app = Flask(__name__)

@app.route('/write_values', methods=["POST"])
def write_values():
    
    data = request.get_json()
    rw_device_manager.add(data)
    
    response = json.dumps(
        {
            "data-accepted": True,
            "current-time": datetime.now().strftime("%d.%m.%Y-%H:%M:%S"),
            "gas-type": "1"
        })
    
    headers = Headers()
    headers.add('Content-Type', 'application/json')
    return Response(response, 200, headers)
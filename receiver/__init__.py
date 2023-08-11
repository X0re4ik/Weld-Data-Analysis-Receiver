import json

from flask import Flask, request, Response
from werkzeug.datastructures import Headers
from datetime import datetime

from receiver.rw_device_manager import rw_device_manager
from receiver.models import Sensor, session

app = Flask(__name__)

@app.route('/write_values', methods=["POST"])
def write_values():
    
    data = request.get_json()
    data["ID"] = rw_device_manager.make_valid_mac_address(data["ID"])
    rw_device_manager.add(data)
    
    response = json.dumps(
        {
            "data-accepted": True,
            "current-time": datetime.now().strftime("%d.%m.%Y-%H:%M:%S"),
            "gas-type": session.query(Sensor).filter(Sensor.mac_address==data["ID"]).first().welding_gas_id
        })
    
    headers = Headers()
    headers.add('Content-Type', 'application/json')
    return Response(response, 200, headers)

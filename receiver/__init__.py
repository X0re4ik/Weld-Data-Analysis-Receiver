from flask import Flask, request
from receiver.rw_device_manager import rw_device_manager


import logging


app = Flask(__name__)

import json

@app.route('/write_values', methods=["POST"])
def write_values():
    if not request.is_json:
        return {
            "success": False
        }

    for i in json.loads(request.get_json()):
        rw_device_manager.add(i)
    
    return {
        "success": True
    }





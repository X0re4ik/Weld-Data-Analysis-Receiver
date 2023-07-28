from flask import Flask, request
from receiver.rw_device_manager import rw_device_manager

app = Flask(__name__)


@app.route('/write_values', methods=["POST"])
def write_values():
    
    if not request.is_json:
        return {}
    data = request.get_json()
    
    rw_device_manager.add(data)
    
    return {
        "success": True
    }





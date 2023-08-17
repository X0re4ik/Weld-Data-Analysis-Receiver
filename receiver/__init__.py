import json

from flask import Flask, request, Response
from flask.views import View
from werkzeug.datastructures import Headers
from datetime import datetime

from receiver.rw_device_manager import rw_device_manager
from receiver.models import Sensor, session
from receiver.configs import ( 
    RECEIVER_USING_PROTOCOL, 
    RECEIVER_USERNAME, RECEIVER_PASSWORD
)

app = Flask(__name__)

class WriteValuesView(View):
    
    methods = ["POST"]
    
    USE_LOGIN: bool
    USERNAME: str
    PASSWORD: str
    
    def check_log_and_pass(self) -> bool:
        if not request.authorization: return False
        valid_username = request.authorization["username"] == self.__class__.USERNAME
        valid_password = request.authorization["password"] == self.__class__.PASSWORD
        return valid_username and valid_password
    
    
    def make_json_response(self, valid: bool = True, error = "", **kwargs) -> str:
        response = {
                "data-accepted": valid,
                "current-time": datetime.now().strftime("%d.%m.%Y-%H:%M:%S"),
                "gas-type": session.query(Sensor).filter(
                    Sensor.mac_address==kwargs["mac_address"]
                    ).first().welding_gas_id if valid else 0     
        }
        
        if not valid: response.update({"error": error})
        
        return json.dumps(response)

    def dispatch_request(self):
        
        """
            request.get_json() == 
                {
                    "ID": "..."
                    "measurements": [
                            {
                                ""
                            }
                        ]
                }
        Returns:
            Response: результат обработки входных значений
        """
        
        headers = Headers()
        headers.add('Content-Type', 'application/json')
        
        if self.__class__.USE_LOGIN and not self.check_log_and_pass():
            return Response(self.make_json_response(False, error="Авторизуйся"), 401, headers)
        
        data = request.get_json()
        if not self.does_json_match_pattern(data):
            return Response(self.make_json_response(False, error="Данные не соответсвуют паттерну"), 400, headers)
        
        data["ID"] = self.make_valid_mac_address(data["ID"])
        
        rw_device_manager.add(data)
        
        return Response(self.make_json_response(mac_address=data["ID"]), 200, headers)



    @staticmethod
    def does_json_match_pattern(dict_: dict) -> bool:
        """does_json_match_pattern
            dict_ должен соответсвовать паттерну
            Например:
                {
                    "ID": "RW:DFDF:RWR934",\n
                    "measurements": [{
                            "time": 1689656864,
                            "amperage": 200,
                            "gas": 50},{
                            "time": 1689656865,
                            "amperage": 212,
                            "gas": 47}
                    ]
                }

        Returns:
            bool: соответвует ли данные патерну
        """
        
        REQUIRED_KEYS = {"ID", "measurements"}
        for KEY in REQUIRED_KEYS:
            if KEY not in dict_: return False
        
        valid_type = isinstance(dict_["measurements"], list) and isinstance(dict_["ID"], str)
        if not valid_type or len(dict_["measurements"]) == 0: return False

        REQUIRED_KEYS_IN_LIST = {"time", "amperage", "gas"}
        for KEY in REQUIRED_KEYS_IN_LIST:
            if KEY not in dict_["measurements"][0]: return False
        return True
    
    @staticmethod
    def make_valid_mac_address(mac_address: str) -> str:
        BLACK_LIST_LETTER = '/:*?"<>|'
        for letter in BLACK_LIST_LETTER:
            mac_address = mac_address.replace(letter, "#")
        return mac_address


app.add_url_rule(
    "/write_values",
    view_func=WriteValuesView.as_view("write-values")
)

WriteValuesView.USE_LOGIN   = RECEIVER_USING_PROTOCOL
WriteValuesView.USERNAME    = RECEIVER_USERNAME
WriteValuesView.PASSWORD    = RECEIVER_PASSWORD

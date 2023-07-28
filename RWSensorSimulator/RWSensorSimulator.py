

import random
import time
from typing import Any
import requests
import json

class WeldingValueGenerator:
    
    
    def __init__(self, duty_cycle: float) -> None:
        if duty_cycle > 1:
            raise RuntimeError("Скважность не может быть больше 1")
        self.__duty_cycle = duty_cycle
    
    def get(self):
        if self.__duty_cycle < random.random():
            amperage = random.randint(150, 500)
            gas = amperage / 10 + random.randint(-5, 5)
        else:
            amperage = random.randint(0, 10)
            gas = random.randint(2, 4)
        return (amperage, gas)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.get()
            

class RWSensorSimulator:
    
    RECORDING_PERIOD = 1
    MAXIMUM_NUMBER_OF_RECORDS = 20
    
    def __init__(self, mac_address, generator=WeldingValueGenerator(0.7)) -> None:
        self.__generator = generator
        self.__mac_address = mac_address
        self.__list_to_send_to_server = []
    
    def _read_values_from_source(self):
        amperage, gas = self.__generator()
        current_time = time.time()
        
        data = {
            "ID": self.__mac_address,
            "time": current_time,
            "amperage": amperage,
            "gas": gas
        }
        
        self.__list_to_send_to_server.append(data)
    
    def _send_to_server(self, ip="localhost", http_port=None, mqtt_port=None, username=None, password=None):
        data = json.dumps(self.__list_to_send_to_server)
        if http_port:
            http_url = f"http://{ip}:{http_port}/write_values"
            r = requests.post(http_url, json=data)
        
        elif mqtt_port:
            from  receiver.mqtt_manager.publisher import MQTTPublisher
            
            def __callback(client):
                topic = f"RW/{self.__mac_address}"
                result = client.publish(topic, data)
            
            MQTTPublisher(
                broker=ip, port=mqtt_port, 
                username=username, password=password, 
                callback=__callback).run()

    def start_simulation(self, ip="localhost", http_port=None, mqtt_port=None, username=None, password=None):
        #print(ip, http_port, mqtt_port, username, password)
        while True:
            if len(self.__list_to_send_to_server) > self.__class__.MAXIMUM_NUMBER_OF_RECORDS:
                self._send_to_server(
                    ip, http_port=http_port, mqtt_port=mqtt_port, 
                    username=username, password=password)
                
                self.__list_to_send_to_server = []
            self._read_values_from_source()
            time.sleep(1)
import json
import os

from dotenv import load_dotenv    
from multiprocessing import Process

from receiver import app
from receiver.mqtt_manager.subscriber import MQTTSubscription
from receiver.rw_device_manager import rw_device_manager


class HTTPServerFastData(Process):
    def run(self) -> None:
        app.run(
            host=os.environ["HOST"],
            port=int(os.environ["HTTP_PORT"]),
            debug=(os.environ["DEBUG"] == '1'))
    

class MQTTServerFastData(Process):
    def run(self) -> None:
        
        def __callback(client, userdata, msg):
            for i in json.loads(msg.payload.decode()):
                rw_device_manager.add(i)
        
        broker      = os.environ["HOST"]
        port        = int(os.environ["MQTT_PORT"])
        username    = os.environ["MQTT_USERNAME"]
        password    = os.environ["MQTT_PASSWORD"]
        
        
        MQTTSubscription(
            broker=broker, port=port, 
            username=username, password=password, 
            callback=__callback).subscribe(os.environ["MQTT_TOPIC"]).run()

 
    
def _main():
    if os.environ["USING_PROTOCOL"] == 'http':
        HTTPServerFastData().start()
    else:
        MQTTServerFastData().start()


load_dotenv(".env")

if __name__ == "__main__":
    _main()
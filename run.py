from collections.abc import Callable, Iterable, Mapping
from typing import Any
from receiver import app

        
from multiprocessing import Process

from receiver.mqtt_manager.subscriber import MQTTSubscription

class HTTPServerFastData(Process):
    
    def run(self) -> None:
        from receiver import app
        app.run(debug=True)
        pass
    
from receiver.rw_device_manager import rw_device_manager
import json
class MQTTServerFastData(Process):
    
    def run(self) -> None:
        
        def __callback(client, userdata, msg):
            for i in json.loads(msg.payload.decode()):
                print(i)
                rw_device_manager.add(i)
        
        MQTTSubscription(broker="localhost", callback=__callback).subscribe("RW/#").run()

 
    
def _main():
    #HTTPServerFastData().start()
    MQTTServerFastData().start()
    

if __name__ == "__main__":
    _main()
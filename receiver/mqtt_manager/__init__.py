from paho.mqtt import client as mqtt_client


class _MQTTManager:
    ID: int = 0
    
    def __init__(self, broker: str, port=1883, username=None, password=None, callback=None) -> None:
        self.__class__.ID += 1
        self.client_id = self.__class__.__name__ + '#' + str(self.__class__.ID)
        self.client = mqtt_client.Client(self.client_id)
        
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.__on_connect
        
        self.client.connect(broker, port)
        
        self._callback = callback
    
    def set_callback(self, callback):
        self._callback = callback
    
    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
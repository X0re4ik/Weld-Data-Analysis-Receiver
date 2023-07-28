from receiver.mqtt_manager import _MQTTManager

from inspect import isfunction


    

class MQTTSubscription(_MQTTManager):
    
    def subscribe(self, topic):
        if not (self._callback and isfunction(self._callback)):
            raise RuntimeError("Коллбек не установлен или не является функцией. Используйте метод set_callback(...)")
        
        self.client.subscribe(topic)
        self.client.on_message = self._callback
        return self
    
    def run(self):
        self.client.loop_forever()
        
        


    
    
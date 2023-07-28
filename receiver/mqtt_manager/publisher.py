from receiver.mqtt_manager import _MQTTManager

from inspect import isfunction

class MQTTPublisher(_MQTTManager):
    
    def run(self):
        if not (self._callback and isfunction(self._callback)):
            raise RuntimeError("Коллбек не установлен или не является функцией. Используйте метод set_callback(...)")
        
        self.client.loop_start()
        self._callback(self.client)
        self.client.loop_stop()
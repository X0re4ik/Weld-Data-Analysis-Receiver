import time
from typing import Dict, Any

from receiver.models import Measurement


class FastData:
    
    ALLOWABLE_INACTIVITY_TIME_IN_SECONDS: int = 2
    
    def __init__(self) -> None:
        self.__template = Measurement.template()
        self.__last_recording_time_UNIX = 0
    
    def is_active(self):
        current_time_UNIX = int(time.time())
        return current_time_UNIX - self.__last_recording_time_UNIX < self.__class__.ALLOWABLE_INACTIVITY_TIME_IN_SECONDS
    
    
    def get(self) -> Dict[str, Any]:
        return {
            "is_active": self.is_active(),
            **self.__template
        }
        
            
        
    
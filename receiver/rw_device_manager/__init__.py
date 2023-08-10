from abc import ABC, abstractmethod
from typing import List, MutableSet, Mapping


from receiver.rw_device_manager.writer_at import WriterAtDailyReport, WriterAtMeasurement
from receiver.rw_device_manager.WeldingValues import WeldingValues
from receiver.rw_device_manager.Timer import Timer


class SensorDataController:
    
    RECORDING_PERIOD_IN_DAILY_REPORT: int = 1000
    
    def __init__(self, ID: str) -> None:
        self.ID = ID
        self.writer_at_daily_report = WriterAtDailyReport()
        self.writer_at_measurement = WriterAtMeasurement()
        
        self.timer = Timer()
        self.timer.start()
        
    
    def send_to_daily_report(self, welding_values: WeldingValues):
        result = self.writer_at_daily_report.write(welding_values)
        
        if self.timer.difference() > self.__class__.RECORDING_PERIOD_IN_DAILY_REPORT:
            result.send()
            self.timer.reset()
        
    def send_to_measurement(self, welding_values: WeldingValues):
        self.writer_at_measurement.write(welding_values).send()
    
    def send_to(self, welding_values: WeldingValues):
        self.send_to_daily_report(welding_values)
        self.send_to_measurement(welding_values)

from queue import Queue
from multiprocessing import Process
from typing import Dict, List

import functools

def _does_dict_match_pattern(pattern):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            dict_ = args[1]
            for key in dict_.keys():
                if not (key in pattern):
                    raise RuntimeError(f"Словарь не соответсвует паттерну {pattern}. Неизвестный ключ: {key}")
        return wrapper
    return decorator

from threading import Thread

class RWDeviceManager:
    
    DEVICE: Dict[str, SensorDataController] = dict()
    
    QUEUE_OF_DATA_TO_BE_PROCESSED: Dict = Queue(maxsize=40)
            
    
    
    
    def _process_element_from_queue(self):
        if self.__class__.QUEUE_OF_DATA_TO_BE_PROCESSED.empty(): return
        
        current_values = self.__class__.QUEUE_OF_DATA_TO_BE_PROCESSED.get()
        
        def treatment(dict_: Dict):
            ID              = dict_["ID"]
            measurements    = dict_["measurements"]
            
            for measurement in measurements:
                time: float        = measurement["time"]
                amperage: float    = measurement["amperage"]
                gas: float         = measurement["gas"]
                
                wv = WeldingValues(
                    ID=ID, 
                    date=time, 
                    amperage=amperage,
                    gas_consumption=gas)
                
                self.__class__.DEVICE[ID].send_to(wv)
            
        Thread(target=treatment, kwargs={
            "dict_": current_values
        }).start()
    
    
    def add(self, dict_: Dict):
        """_summary_

        Args:
            list_ (List[Dict]): _description_
        """
        
        dict_["ID"] = self.make_valid_mac_address(dict_["ID"])
        ID = dict_["ID"]
        if ID not in self.__class__.DEVICE.keys():
            self.__class__.DEVICE[ID] = SensorDataController(ID)
        
        self.__class__.QUEUE_OF_DATA_TO_BE_PROCESSED.put(dict_)
        self._process_element_from_queue()

    @staticmethod
    def make_valid_mac_address(mac_address: str) -> str:
        BLACK_LIST_LETTER = '/:*?"<>|'
        for letter in BLACK_LIST_LETTER:
            mac_address = mac_address.replace(letter, "#")
        return mac_address

   
rw_device_manager = RWDeviceManager()
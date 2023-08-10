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

class RWDeviceManager:
    
    
    DEVICE = dict()
    
    QUEUE_OF_DATA_TO_BE_PROCESSED = Queue(maxsize=30)
    
    
    def _process_element_from_queue(self):
        if self.__class__.QUEUE_OF_DATA_TO_BE_PROCESSED.empty(): return
        
        current_value = self.__class__.QUEUE_OF_DATA_TO_BE_PROCESSED.get()
        
        def treatment(welding_values: WeldingValues):
            self.__class__.DEVICE[welding_values.ID].send_to(welding_values)
            
        proccess_1 = Process(target=treatment, kwargs={
            "welding_values": current_value
        }, daemon=True)
        proccess_1.run()
        

    def add(self, data_in_dict_format):
        
        if self._does_data_match_pattern(data_in_dict_format):
            ID = data_in_dict_format["ID"]
            wv = WeldingValues(
                ID=ID, 
                date=data_in_dict_format["time"], 
                amperage=data_in_dict_format["amperage"],
                gas_consumption=data_in_dict_format["gas"])
            
            if ID not in self.__class__.DEVICE:
                self.__class__.DEVICE[ID] = SensorDataController(ID)
            
            if self.__class__.QUEUE_OF_DATA_TO_BE_PROCESSED.qsize() == self.__class__.QUEUE_OF_DATA_TO_BE_PROCESSED.maxsize:
                print("")
            self.__class__.QUEUE_OF_DATA_TO_BE_PROCESSED.put(wv)
            self._process_element_from_queue()
        

    def _does_data_match_pattern(self, data: Mapping):
        options = {'time', 'ID', 'amperage', 'gas'}
        for key in data.keys():
            if not (key in options):
                return False
        return True
            


   
rw_device_manager = RWDeviceManager()
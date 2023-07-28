from abc import ABC, abstractmethod
from typing import List, MutableSet, Mapping


from receiver.rw_device_manager.writer_at import WriterAtDailyReport, WriterAtMeasurement
from receiver.rw_device_manager.WeldingValues import WeldingValues
from receiver.rw_device_manager.Timer import Timer


class SensorDataController:
    
    RECORDING_PERIOD_IN_DAILY_REPORT: int = 1000
    RECORDING_PERIOD_IN_MEASUREMENT: int = 1000
    
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


class RWDeviceManager:
    
    
    DEVICE = dict()

    
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
            
            self.__class__.DEVICE[ID].send_to(wv)
        

    def _does_data_match_pattern(self, data: Mapping):
        options = {'time', 'ID', 'amperage', 'gas'}
        for key in data.keys():
            if not (key in options):
                return False
        return True
            


   
rw_device_manager = RWDeviceManager()
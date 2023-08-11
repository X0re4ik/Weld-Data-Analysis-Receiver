from abc import ABC
from typing import Tuple
from datetime import datetime 
from sqlalchemy.sql import and_

from receiver.models import session
from receiver.models import DailyReport, Measurement



from receiver.rw_device_manager.WeldingValues import WeldingValues        

class _WriterAtTable(ABC):
    
    def __init__(self, __table = None) -> None:
        self.__table = __table
        self.reset_values()
        
    def reset_values(self):
        """reset_values (сброс параметров)
        Параметры переводятся в значения по умолчанию, в частности template еквивалентно Table.template()
        """
        self.template = self.__table.template()
        self.__permission_to_write_to_table = False
    
    def write(self, values: WeldingValues):
        self.template["sensor_id"] = values.get_sensor_id()
        self._set_permission(True)
        
        for i in dir(self):
            result = getattr(self, i)
            if i.startswith(f'_{self.__class__.__name__}__update') and hasattr(result, '__call__'):
                result(values)
        
        return self

    def send(self) -> None:
        if not self.__permission_to_write_to_table:
            raise RuntimeError(
                "Нет разрешения на отправку данных в таблицу"
            )
        self._set_permission(False)
        
    def _set_permission(self, condition: bool):
        self.__permission_to_write_to_table = condition


    




class WriterAtDailyReport(_WriterAtTable):
    """WriterAtDailyReport
        Класс для контроля и записи данных в таблицу "DailyReport"
        Основными методами пользования являются write(...) и send(...)
        
    """
    
    
    def __init__(self) -> None:
        _WriterAtTable.__init__(self, DailyReport)
        
    def send(self):
        super().send()
        existed, daily_report = WriterAtDailyReport.creat_if_not_exist(self.template["sensor_id"], self.template["date"])
        
        if not existed:
            self.reset_values()
        
        daily_report.average_amperage = self.template["average_amperage"]
        daily_report.average_gas_consumption = self.template["average_gas_consumption"]
        daily_report.average_wire_consumption = self.template["average_wire_consumption"]
        
        daily_report.expended_gas = self.template["expended_gas"]
        daily_report.expended_wire = self.template["expended_wire"]
        
        daily_report.max_amperage = self.template["max_amperage"]
        daily_report.max_gas_consumption = self.template["max_gas_consumption"]
        daily_report.max_wire_consumption = self.template["max_wire_consumption"]
        
        daily_report.weld_metal_id = self.template["weld_metal_id"]
        daily_report.welding_wire_diameter_id = self.template["welding_wire_diameter_id"]
        
        daily_report.worker_id = self.template["worker_id"]
        daily_report.running_time_in_seconds = self.template["running_time_in_seconds"]
        daily_report.idle_time_in_seconds = self.template["idle_time_in_seconds"]
        daily_report.welding_gas_id = self.template["welding_gas_id"]
        
        session.begin()
        session.commit()
        
        return self
    
    
      
    def __update_date(self, values: WeldingValues):
        self.template["date"] = values.UTC_time()
        
        
    def __update_consumption(self, values: WeldingValues):
        if not values.is_useful_data(): return
        amperage, gas_consumption, wire_consumption = values.get()
        
        self.template["expended_wire"] += gas_consumption / 3600
        self.template["expended_gas"] += wire_consumption / 60
        
        
    def __update_foreign_keys(self, values: WeldingValues):
        worker_id, welding_wire_diameter_id, weld_metal_id = values.welding_parameters.get_foreign_keys()
        
        self.template["worker_id"] = worker_id
        self.template["welding_wire_diameter_id"] = welding_wire_diameter_id
        self.template["weld_metal_id"] = weld_metal_id

    
    def __update_average(self, values: WeldingValues):
        if not values.is_useful_data(): return
        
        amperage, gas_consumption, wire_consumption = values.get()
        
        self.template["average_amperage"]            = (self.template["average_amperage"] + amperage) / 2
        self.template["average_gas_consumption"]     = (self.template["average_gas_consumption"] + gas_consumption) / 2
        self.template["average_wire_consumption"]    = (self.template["average_wire_consumption"] + wire_consumption) / 2
        
    def __update_maximum(self, values: WeldingValues):
        if not values.is_useful_data(): return
        amperage, gas_consumption, wire_consumption = values.get()
        
        self.template["max_amperage"]            = max(self.template["max_amperage"], amperage)
        self.template["max_gas_consumption"]     = max(self.template["max_gas_consumption"], gas_consumption)
        self.template["max_wire_consumption"]    = max(self.template["max_wire_consumption"], wire_consumption)
            
    def __update_time_in_seconds(self, values: WeldingValues):
        if values.is_useful_data():
            self.template["running_time_in_seconds"] += 1
        else:
            self.template["idle_time_in_seconds"] += 1
            
    @staticmethod
    def creat_if_not_exist(sensor_id, date: datetime) -> Tuple[bool, DailyReport]:
        daily_report = session.query(DailyReport).filter(and_(
            DailyReport.date==date.date(),
            DailyReport.sensor_id==sensor_id)).first()
        
        if not daily_report:
            template = DailyReport.template()
            template["sensor_id"] = sensor_id
            template["date"] = date
            
            new_daily_report = DailyReport(**template)
            session.begin()
            session.add(new_daily_report)
            session.commit()
            return (False, new_daily_report)
        
        return True, daily_report

            
                
     
        

class WriterAtMeasurement(_WriterAtTable):
    
    def __init__(self) -> None:
        _WriterAtTable.__init__(self, Measurement)
        self.is_useful_data = False
        
    def send(self):
        super().send()
        if "self.is_useful_data":
            measurement = Measurement(**self.template)
            session.begin()
            session.add(measurement)
            session.commit()
            
    def __update_vales(self, values: WeldingValues):
        amperage, gas_consumption, wire_consumption = values.get()
        
        self.is_useful_data = values.is_useful_data()
        self.template["utc_time"] = values.UTC_time()
        self.template["amperage"] = amperage
        self.template["gas_consumption"] = gas_consumption
        self.template["wire_consumption"] = wire_consumption
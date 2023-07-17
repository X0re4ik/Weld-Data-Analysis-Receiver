from Writer.models import session
from Writer.models import (Sensor, DailyReport, WeldingWireDiameter, WeldMetal, Worker, Measurement)



from abc import ABC, abstractmethod
from typing import List, MutableSet, Mapping




import math

class WeldingCalculator():
    @staticmethod
    def wire_feed_speed(I: float, D: float, 
                        steel_density: float, melting_factor: float = 14.0):
        """_summary_

        Args:
            I (float): текущая сила тока [А]
            D (float): диаметр сварочной проволки [мм]
            steel_density (float): плотность свариваемой поверхности [?]
            melting_factor (float, optional):  коэффициент расплавления [г/А·ч]. Defaults to 14.0 (для постоянного тока обратной полярности).

        Returns:
            float: требуемая скорость подачи проволки [м/ч]
        """
 
        # ross_sectional_area_welding_wire (Fп = π×dп2/4) – площадь поперечного сечения сварочной проволоки [мм2]
        cross_sectional_area_welding_wire = math.pi * math.pow(D, 2) / 4
        return float((melting_factor * I) /  (cross_sectional_area_welding_wire * steel_density))


    @staticmethod
    def __wire_consumption(
        wire_feed_speed: float, 
        welding_wire_weight: float):
        """_summary_

        Args:
            wire_feed_speed (float): необходимая скорость подачи проволки [м/ч]
            welding_wire_weight (float): вес сварочной проволки [кг/м].

        Returns:
            _type_: _description_
        """
        return wire_feed_speed * welding_wire_weight
    
    @staticmethod
    def welding_wire_weight(D: float, steel_density: float, length: float = 1):
        return (math.pi * math.pow(D, 2) / 4) * steel_density * length
    
    @staticmethod
    def wire_consumption(I: float, D: float, 
                        steel_density: float, melting_factor: float = 14.0):
        _wire_feed_speed = WeldingCalculator.wire_feed_speed(I, D, steel_density, melting_factor)
        _welding_wire_weight = WeldingCalculator.welding_wire_weight(D, steel_density, 1)
        return WeldingCalculator.__wire_consumption(_wire_feed_speed, _welding_wire_weight)
    
    
class WeldingParameters:
    def __init__(self, mac_address) -> None:
        self.sensor = WeldingParameters.creat_if_not_exist()
        
        
        
        self.welding_wire_diameter = session.query(WeldingWireDiameter).filter_by(id=self.sensor.welding_wire_diameter_id).first()
        self.diameter = self.welding_wire_diameter.diameter
        
        self.weld_metal = session.query(WeldMetal).filter_by(id=self.sensor.weld_metal_id).first()
        self.steel_density = self.weld_metal.density
        
        self.worker_id = self.sensor.worker_id
    
    def get_foreign_keys(self):
        return (self.worker_id, self.welding_wire_diameter.id, self.weld_metal.id)
    
    @staticmethod
    def creat_if_not_exist(mac_address: str):
        sensor = session.query(Sensor).filter_by(mac_address=mac_address).first()
        if not sensor:
            template = Sensor.template()
            template["mac_address"] = mac_address
            template["device_name"] = mac_address
            
            new_sensor = Sensor(**template)
            session.begin()
            session.add(new_sensor)
            session.commit()
            return new_sensor

class WeldingValues:
    
    LIMIT_AMPERAGE = 25,
    LIMIT_GAS_CONSUMPTION = 5
    
    def __init__(self, ID, date, amperage: int, gas_consumption: int) -> None:
        self.ID: str = ID
        self.date: int = date
        self.amperage: float = amperage
        self.welding_parameters = WeldingParameters(ID)
        self.gas_consumption: float = gas_consumption
        self.wire_consumption: float = self._calculate_wire_consumption()
        
    
    
    def is_useful_data(self) -> bool:
        return (self.amperage > self.__class__.LIMIT_AMPERAGE and self.gas_consumption > self.__class__.LIMIT_GAS_CONSUMPTION)
    
    def get(self):
        return (self.amperage, self.gas_consumption, self.wire_consumption)
    
    def _calculate_wire_consumption(self):
        return WeldingCalculator.wire_consumption(
            I=self.amperage,
            D=self.welding_parameters.diameter,
            steel_density=self.welding_parameters.steel_density,
        )
        
        

class _RWDeviceDatabaseAssistant:
    
    def __init__(self) -> None:
        self.reset_values()
         
    def reset_values(self):
        self.sensor = None
        self.__permission_to_write_to_table = False
    
    def write(self, values: WeldingValues):
        self._load_sensor()
        self._set_permission(True)

    def send(self):
        if not self.permission_to_write_to_table:
            raise RuntimeError(
                "Нет разрешения на отправку данных в таблицу"
            )
        self._set_permission(False)
    
    def _load_sensor(self, values: WeldingValues):
        self.sensor = values.welding_parameters.sensor
        
    def _set_permission(self, condition: bool):
        self.__permission_to_write_to_table = condition


    

    


        
    
    
from datetime import date

class WriterAtDailyReport(_RWDeviceDatabaseAssistant):

    @staticmethod
    def creat_if_not_exist(sensor_id, date) -> DailyReport:
        daily_report = session.query(DailyReport).filter_by(
            date=date,
            sensor_id=sensor_id).first()

        if not daily_report:
            template = DailyReport.template()
            template["sensor_id"] = sensor_id,
            template["date"] = date
            new_daily_report = DailyReport(**template)
            session.begin()
            session.add(new_daily_report)
            session.commit()
            return new_daily_report
        
        return daily_report
    
 
    def reset_values(self):
        super().reset_all_values()
        
        creat_dict = lambda options, fill=0: dict(zip(options, [fill]*len(options)))
        
        self.average             = creat_dict(["amperage", "gas_consumption", "wire_consumption"])
        self.consumption                = creat_dict(["gas", "wire"])
        self.time_in_seconds            = creat_dict(["running", "idle"])
        self.foreign_keys               = creat_dict(["weld_metal", "welding_wire_diameter", "welder"], fill=1)
        self.foreign_keys["welder"] = None
        
        self.maximum             = creat_dict(["amperage", "gas_consumption", "wire_consumption"])
        
    def write(self, values: WeldingValues):
        super().write(values)
        
        for i in dir(self):
            result = getattr(self, i)
            if i.startswith('_WriterAtDailyReport__update') and hasattr(result, '__call__'):
                result(values)
        
        
        
            
    def send(self):
        super().send()
        
        daily_report = WriterAtDailyReport.creat_if_not_exist(self.sensor.id, date.today())
        
        daily_report.average_amperage           = self.average["amperage"]
        daily_report.average_gas_consumption    = self.average["gas_consumption"]
        daily_report.average_wire_consumption   = self.average["wire_consumption"]
        
        daily_report.expended_wire              = self.consumption["gas"]
        daily_report.expended_gas               = self.consumption["wire"]
        
        daily_report.max_amperage               = self.maximum["amperage"]
        daily_report.max_gas_consumption        = self.maximum["gas_consumption"]
        daily_report.max_wire_consumption       = self.maximum["wire_consumption"]
        
        daily_report.worker_id                  = self.foreign_keys["welder"]
        daily_report.welding_wire_diameter_id   = self.foreign_keys["welding_wire_diameter"]
        daily_report.weld_metal_id              = self.foreign_keys["weld_metal"]
        
        daily_report.running_time_in_seconds    = self.time_in_seconds["running"]
        daily_report.idle_time_in_seconds       = self.time_in_seconds["idle"]
        
        session.begin()
        session.add(daily_report)
        session.commit()
        

        
    def __update_consumption(self, values: WeldingValues):
        if not self.is_useful_data(values): return
        amperage, gas_consumption, wire_consumption = values.get()
        
        self.consumption["gas"] += gas_consumption / 3600
        self.consumption["wire"] += wire_consumption / 60
        
        
    def __update_foreign_keys(self, values: WeldingValues):
        worker_id, welding_wire_diameter_id, weld_metal_id = values.get_foreign_keys()
        
        self.foreign_keys["welder"] = worker_id
        self.foreign_keys["welding_wire_diameter"] = welding_wire_diameter_id
        self.foreign_keys["weld_metal"] = weld_metal_id

    
    def __update_average(self, values: WeldingValues):
        if not self.is_useful_data(values): return
        
        amperage, gas_consumption, wire_consumption = values.get()
        
        self.average["amperage"]            = (self.average["amperage"] + amperage) / 2
        self.average["gas_consumption"]     = (self.average["gas_consumption"] + gas_consumption) / 2
        self.average["wire_consumption"]    = (self.average["wire_consumption"] + wire_consumption) / 2
        
    def __update_maximum(self, values: WeldingValues):
        if not self.is_useful_data(values): return
        amperage, gas_consumption, wire_consumption = values.get()
        
        self.maximum["amperage"]            = max(self.maximum["amperage"], amperage)
        self.maximum["gas_consumption"]     = max(self.maximum["gas_consumption"], gas_consumption)
        self.maximum["wire_consumption"]    = max(self.maximum["wire_consumption"], wire_consumption)
            
    def __update_time_in_seconds(self, values: WeldingValues):
        if self.is_useful_data(values):
            self.time_in_seconds["running"] += 1
        else:
            self.time_in_seconds["idle"] += 1

            
                
     
        

class WriterAtMeasurement(_RWDeviceDatabaseAssistant):
    
    def reset_values(self):
        super().reset_values()
        creat_dict = lambda options, fill=0: dict(zip(options, [fill]*len(options)))
        self.values = creat_dict(["amperage", "gas_consumption", "wire_consumption"])
        
        self.is_valid = False

        

    def write(self, values: WeldingValues):
        super().write(values)
        amperage, gas_consumption, wire_consumption = values.get()
        
        self.is_valid = values.is_useful_data()
        self.values["amperage"] = amperage
        self.values["gas_consumption"] = gas_consumption
        self.values["wire_consumption"] = wire_consumption
        
        
    
    def send(self):
        super().write()
        if self.is_valid:
            measurement = Measurement(
                sensor_id = self.sensor.id,
                amperage = self.values["amperage"],
                gas_consumption = self.values["gas_consumption"],
                wire_consumption = self.values["wire_consumption"]
            )
            session.begin()
            session.add(measurement)
            session.commit()
        
        


        

        

print(_RWDeviceDatabaseAssistant.creat_if_not_exist("uy823y423er3r31"))
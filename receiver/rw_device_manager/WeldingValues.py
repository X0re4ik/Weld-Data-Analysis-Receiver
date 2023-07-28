from receiver.models import session
from receiver.models import (Sensor, DailyReport, WeldingWireDiameter, WeldMetal, Worker, Measurement)



from abc import ABC, abstractmethod
from typing import List, MutableSet, Mapping
from datetime import datetime 

import math


class WeldingCalculator:
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
        """WeldingCalculator.__wire_consumption

        Args:
            wire_feed_speed (float): необходимая скорость подачи проволки [м/ч]
            welding_wire_weight (float): вес сварочной проволки [кг/м]

        Returns:
            float: расход проволки [кг/час]
        """
        return wire_feed_speed * welding_wire_weight
    
    @staticmethod
    def welding_wire_weight(D: float, steel_density: float, length: float = 1):
        return (math.pi * math.pow(D, 2) / 4) * steel_density * length
    
    @staticmethod
    def wire_consumption(I: float, D: float, 
                        steel_density: float, melting_factor: float = 14.0) -> float:
        """\nWeldingCalculator.__wire_consumption

        Args:
            I (float): текущая сила тока [А]\n
            D (float): диаметр сварочной проволки [мм]\n
            steel_density (float): плотность свариваемой поверхности [?]\n
            melting_factor (float, optional):  коэффициент расплавления [г/А·ч]. Defaults to 14.0 (для постоянного тока обратной полярности).

        Returns:
            float: расход проволки [кг/час]
        """
        _wire_feed_speed = WeldingCalculator.wire_feed_speed(I, D, steel_density, melting_factor)
        _welding_wire_weight = WeldingCalculator.welding_wire_weight(D, steel_density, 1)
        return WeldingCalculator.__wire_consumption(_wire_feed_speed, _welding_wire_weight)
    


class WeldingParameters:
    def __init__(self, mac_address) -> None:
        self.sensor = WeldingParameters.creat_if_not_exist(mac_address)

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
        return sensor

class WeldingValues:
    
    LIMIT_AMPERAGE = 25
    LIMIT_GAS_CONSUMPTION = 5
    
    def __init__(self, ID, date, amperage: int, gas_consumption: int) -> None:
        self.ID: str = ID
        self.date: int = date
        self.amperage: float = amperage
        self.gas_consumption: float = gas_consumption
        self.welding_parameters = WeldingParameters(ID)
        
        self.wire_consumption: float = self._calculate_wire_consumption()
        
        
        
    
    def get_sensor_id(self):
        return self.welding_parameters.sensor.id
    
    def UTC_time(self):
        return datetime.fromtimestamp(self.date)
    
    def is_useful_data(self) -> bool:
        return (self.amperage > self.__class__.LIMIT_AMPERAGE) and (self.gas_consumption > self.__class__.LIMIT_GAS_CONSUMPTION)
    
    def get(self):
        return (self.amperage, self.gas_consumption, self.wire_consumption)
    
    def _calculate_wire_consumption(self):
        return WeldingCalculator.wire_consumption(
            I=self.amperage,
            D=self.welding_parameters.diameter,
            steel_density=self.welding_parameters.steel_density,
        )
  
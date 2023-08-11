from sqlalchemy import *
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base


from receiver.configs import DB_URI
 
Base = declarative_base()
engine = create_engine(DB_URI)
metadata = MetaData(bind=engine)

from sqlalchemy.orm import create_session
session = create_session(bind=engine)


def merge(options, values):
    assert len(options) == len(values), f'length of the array "options" must equal the length of the array "values"'
    return dict(zip(options, values))
 

class Sensor(Base):
    __table__ = Table('sensor', metadata, autoload=True)
    
    @staticmethod
    def template():
        options = ["mac_address", "device_name", "location", "measurement_period", "begining_of_work_day", "end_of_working_day", "welding_wire_diameter_id", "weld_metal_id", "welding_gas_id"]
        values = [None , None, None, 1, 6, 18, 1, 1, 1]
        return merge(options, values)

class Worker(Base):
    __table__ = Table('worker', metadata, autoload=True)

class Master(Base):
    __table__ = Table('master', metadata, autoload=True)
    
class Welder(Base):
    __table__ = Table('welder', metadata, autoload=True)

class WeldingWireDiameter(Base):
    __table__ = Table('welding_wire_diameter', metadata, autoload=True)
        
class WeldMetal(Base):
    __table__ = Table('weld_metal', metadata, autoload=True)
        
class Measurement(Base):
    __table__ = Table('measurement', metadata, autoload=True)
    
    @staticmethod
    def template():
        return merge(
            ["sensor_id", "utc_time", 
             "amperage", "gas_consumption", "wire_consumption"],
            [None, None, 0, 0, 0])
    
    
class DailyReport(Base):
    __table__ = Table('daily_report', metadata, autoload=True)
    
    
    @staticmethod
    def template():
        return merge(
            ["sensor_id", "date", 
             "average_amperage", "average_gas_consumption", "average_wire_consumption", 
             "expended_wire", "expended_gas", 
             "max_amperage", "max_gas_consumption", "max_wire_consumption", 
             "worker_id", "welding_wire_diameter_id", "weld_metal_id", "welding_gas_id",
             "running_time_in_seconds", "idle_time_in_seconds"], 
            [ None, None,
             0, 0, 0,
             0, 0,
             0, 0, 0,
             None, 1, 1, 1,
             0, 0
            ]
            )
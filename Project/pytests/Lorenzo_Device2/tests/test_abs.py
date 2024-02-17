import math
from .. import  ABS

def test_abs_brake_pedal_pressure_change():
    abs_system = ABS()
    abs_system.change_brake_pedal_pressure(10)
    assert abs_system.brakePedalPressure == 10


def test_abs_brake_actual_pressure_change():
    abs_system = ABS()
    abs_system.change_brake_pedal_pressure(10)
    assert abs_system.brakeActualPressure == 60

def test_abs_change_wheels_speed():
    time = 1
    abs_system = ABS()
    abs_system.change_wheels_speed(time)
    for i in range (0, 4):
        assert abs_system.wheels[i].speed == int(2 * math.log(time+1))

def test_abs_change_wheels_speed():
    abs_system = ABS()
    abs_system.brakePedalPressure == 10
    abs_system.change_wheels_speed(1)
    for i in range (0, 4):
        assert abs_system.wheels[i].speed == 1

def test_abs_wheels_fluid_temperature():
    time = 1
    abs_system = ABS()
    abs_system.brakePedalPressure == 10
    oldFT = []
    for i in range(0, 4):
        oldFT.append(abs_system.wheels[i].fluidTemperature)
    abs_system.change_wheels_speed(time)
    for i in range (0, 4):
        assert abs_system.wheels[i].fluidTemperature == oldFT[i]-int( math.log(time+1))

def test_abs_wheels_disk_temperature():
    time = 1
    abs_system = ABS()
    abs_system.brakePedalPressure == 10
    oldDT = []
    for i in range(0, 4):
        oldDT.append(abs_system.wheels[i].diskTemperature)
    abs_system.change_wheels_speed(time)
    for i in range (0, 4):
        assert abs_system.wheels[i].diskTemperature == oldDT[i]-int(3 * math.log(time+1))

def test_abs_get_info():
    abs_system = ABS()
    time = 1
    assert abs_system.get_info(time) == {
            "BrakePedalPressure" : abs_system.brakePedalPressure,
            "BrakeActualPressure": abs_system.brakeActualPressure,
            "TractionControl" : abs_system.tractionControl,
            "Wheel1" : {
                "Speed" : int(abs_system.wheels[0].speed),
                "Pressure" : abs_system.wheels[0].pressure,
                "FluidTemperature": abs_system.wheels[0].fluidTemperature,
                "DiskTemperature": abs_system.wheels[0].diskTemperature
            },
            "Wheel2" : {
                "Speed" : int(abs_system.wheels[1].speed),
                "Pressure" : abs_system.wheels[1].pressure,
                "FluidTemperature": abs_system.wheels[1].fluidTemperature,
                "DiskTemperature": abs_system.wheels[1].diskTemperature
            },
            "Wheel3" : {
                "Speed" : int(abs_system.wheels[2].speed),
                "Pressure" : abs_system.wheels[2].pressure,
                "FluidTemperature": abs_system.wheels[2].fluidTemperature,
                "DiskTemperature": abs_system.wheels[2].diskTemperature
            },
            "Wheel4" : {
                "Speed" : int(abs_system.wheels[3].speed),
                "Pressure" : abs_system.wheels[3].pressure,
                "FluidTemperature": abs_system.wheels[3].fluidTemperature,
                "DiskTemperature": abs_system.wheels[3].diskTemperature
            }   
        }

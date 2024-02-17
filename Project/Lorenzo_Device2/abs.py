import math

class Wheel:
    def __init__(self, speed, pressure):
        self.speed = speed #int
        self.pressure = pressure #int
        self.fluidTemperature = 10
        self.diskTemperature = 30

    def increase_wheel_speed(self, time):
        speed = self.speed + int(2 * math.log(time+1))
        if speed<140:
            self.speed=speed
        else:
            self.speed=140
        fluidTemperature=self.fluidTemperature-int( math.log(time+1))
        if self.fluidTemperature>0:
            self.fluidTemperature=fluidTemperature
        else:
            self.fluidTemperature=0
        diskTemperature=self.diskTemperature-int(3 * math.log(time+1))
        if self.diskTemperature>0:
            self.diskTemperature=diskTemperature
        else:
            self.diskTemperature=0
        return self
    
    def decrease_wheel_speed(self, time):
        speed=self.speed -3
        if speed > 0:
            self.speed = speed
        else:
            self.speed = 0
        fluidTemperature=self.fluidTemperature+int(2 * math.log(time+1)/1.5)
        if self.fluidTemperature<40:
            self.fluidTemperature=fluidTemperature
        else:
            self.fluidTemperature=40
        diskTemperature=self.diskTemperature+int(4 * math.log(time+1)/1.5)
        if self.diskTemperature<200:
            self.diskTemperature=diskTemperature
        else:
            self.diskTemperature=200
        return self

    
class ABS:
    def __init__(self):
        self.wheels = [Wheel(0, 3), Wheel(0, 3), Wheel(0, 3), Wheel(0, 3)]
        self.brakePedalPressure = 0
        self.brakeActualPressure = 0
        self.tractionControl = False

    def change_wheels_speed(self, time):
        if self.brakePedalPressure == 0:
            for i in range (0, 4):
                self.wheels[i] = self.wheels[i].increase_wheel_speed(time)
        else:
            for i in range (0, 4):
                self.wheels[i] = self.wheels[i].decrease_wheel_speed(time)
        return self
    
    def change_brake_pedal_pressure(self, time):
        if time != 0 and time%10 == 0:
            self.brakePedalPressure = 10
            self.brakeActualPressure = 60
        elif time%5 == 0:
            self.brakePedalPressure = 0
            self.brakeActualPressure = 0

        return self
    
    def get_info(self, time):
        self.tractionControl = False
        self = self.change_wheels_speed(time)
        self = self.change_brake_pedal_pressure(time)
        return {
            "BrakePedalPressure" : self.brakePedalPressure,
            "BrakeActualPressure": self.brakeActualPressure,
            "TractionControl" : self.tractionControl,
            "Wheel1" : {
                "Speed" : int(self.wheels[0].speed),
                "Pressure" : self.wheels[0].pressure,
                "FluidTemperature": self.wheels[0].fluidTemperature,
                "DiskTemperature": self.wheels[0].diskTemperature
            },
            "Wheel2" : {
                "Speed" : int(self.wheels[1].speed),
                "Pressure" : self.wheels[1].pressure,
                "FluidTemperature": self.wheels[1].fluidTemperature,
                "DiskTemperature": self.wheels[1].diskTemperature
            },
            "Wheel3" : {
                "Speed" : int(self.wheels[2].speed),
                "Pressure" : self.wheels[2].pressure,
                "FluidTemperature": self.wheels[2].fluidTemperature,
                "DiskTemperature": self.wheels[2].diskTemperature
            },
            "Wheel4" : {
                "Speed" : int(self.wheels[3].speed),
                "Pressure" : self.wheels[3].pressure,
                "FluidTemperature": self.wheels[3].fluidTemperature,
                "DiskTemperature": self.wheels[3].diskTemperature
            }   
        }
    
    def get_name(self):
        return "ABS"

        

        
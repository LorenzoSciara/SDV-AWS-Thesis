import math

class Battery:
    def __init__(self):
        self.energyAdded=round(0, 2)
        self.stateOfCharge=round(100, 2)
        self.batteryTemperature=0
        self.isAcellerate = True

    def acellerate(self, time):
        stateOfCharge = round(self.stateOfCharge - (time%10/5), 2)
        if self.stateOfCharge>=1:    
            self.stateOfCharge = stateOfCharge
            self.batteryTemperature = int(50 +5 * math.sin(time))    
        else:
            self.stateOfCharge=0  
        return self
    
    def decellerate(self, time):
        stateOfCharge = round(self.stateOfCharge + (time%10/10), 2)
        if self.stateOfCharge<100:
            self.stateOfCharge = stateOfCharge
            self.batteryTemperature = int(50 +5 * math.sin(time))
            self.energyAdded = round(self.energyAdded + (time%10/10), 2)
        else:
            self.stateOfCharge=100
        return self
    
    def get_info(self, time):
        if time != 0 and time%10 == 0:
            self.isAcellerate = False
        elif time%5 == 0:
            self.isAcellerate = True

        if self.isAcellerate == True:
            self = self.acellerate(time)
        else:
            self = self.decellerate(time)
        return {
            "StateOfCharge" : self.stateOfCharge,
            "BatteryTemperature": self.batteryTemperature,
            "EnergyAdded" : self.energyAdded,
        }
    
    def get_name(self):
        return "Battery"

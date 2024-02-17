class Engine:
    def __init__(self):
        self.acelleratorPedalPosition = 0
        self.accelerationEfficiency=0
        self.brakeRegenerationEfficiency=0
        self.rpm = 500
        self.gear = 1
        self.isAcellerate = True

    def acellerate(self, time):
        
        self.acelleratorPedalPosition = int(self.acelleratorPedalPosition + (time%10/2))
        self.accelerationEfficiency = 50
        self.brakeRegenerationEfficiency = 0
        if self.acelleratorPedalPosition > 45:
            self.acelleratorPedalPosition = 45

        self.rpm = self.rpm+int(50*self.acelleratorPedalPosition)
        if self.rpm > 3000:
            if self.gear < 6:
                self.gear = self.gear + 1
                self.rpm = 1000
            else:
                self.gear = 6
                if self.rpm > 3500:
                    self.rpm = 3500
        return self
    
    def decellerate(self, time):
        self.acelleratorPedalPosition = 0
        self.accelerationEfficiency = 0
        self.brakeRegenerationEfficiency = 40
        self.rpm = self.rpm-300
        if self.rpm < 1000:
            if self.gear > 1:
                self.gear = self.gear-1
                self.rpm = 1500
            else:
                self.gear = 1
                if self.rpm < 500:
                    self.rpm = 500
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
            "AcelleratorPedalPosition" : self.acelleratorPedalPosition,
            "AccelerationEfficiency": self.accelerationEfficiency,
            "BrakeRegenerationEfficiency": self.brakeRegenerationEfficiency,
            "RPM" : self.rpm,
            "Gear" : self.gear,   
        }
    
    def get_name(self):
        return "Engine"


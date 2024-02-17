import math

class Zone:
    def __init__(self, state, temperature, humidity):
        self.state = state #heat/cool
        self.temperature = temperature #int
        self.oldTemperature = 0
        self.humidity = round(humidity, 2) #float

    def auto_change_temperature(self, time):
        if time > 5:
            self.oldTemperature = self.temperature
            self.temperature = 25 +5 * math.sin(time/10)
            if self.temperature < 20:
                self.oldTemperature = self.temperature
                self.temperature = 20
            elif self.temperature > 30:
                self.oldTemperature = self.temperature
                self.temperature = 30
        else: 
            self.oldTemperature = self.temperature
            self.temperature = self.temperature +5 * math.sin(time/10)

        if self.temperature > self.oldTemperature:
            self.state = "heat"
        else:
            self.state = "cool"
        return self

    def auto_change_humidity(self, time):
        self.humidity = round(30 + 2 * math.sin(time), 2)
        if self.humidity < 29:
            self.humidity = round(29, 2)
        elif self.humidity > 31:
            self.humidity = round(31, 2)
        return self

class AirConditioning:
    def __init__(self):
        self.zones = [Zone("heat", 18, 30), Zone("heat", 20, 30), Zone("heat", 20, 30)]

    def auto_change_temperature(self, time):
        for i in range(0, 3):
            self.zones[i] = self.zones[i].auto_change_temperature(time)
        return self


    def auto_change_humidity(self, time):
        for i in range(0, 3):
            self.zones[i] = self.zones[i].auto_change_humidity(time)
        return self
    
    def get_info(self, time):
        self = self.auto_change_temperature(time)
        self = self.auto_change_humidity(time)

        return {
        "Zone1" : {
        "State" : self.zones[0].state,
        "Temperature" : int(self.zones[0].temperature),
        "Humidity" : self.zones[0].humidity
        },
        "Zone2" : {
            "State" : self.zones[1].state,
            "Temperature" : int(self.zones[1].temperature),
            "Humidity" : self.zones[1].humidity
        },
        "Zone3" : {
            "State" : self.zones[2].state,
            "Temperature" : int(self.zones[2].temperature),
            "Humidity" : self.zones[2].humidity
        }
    }

    def get_name(self):
        return "AirConditioning"
    
    
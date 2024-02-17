import math

class HeatedSeat:
    def __init__(self, state, temperature):
        self.state = state #heat/cool
        self.temperature = temperature #int
        self.oldTemperature = 0

    def change_temperature(self, time):
            self.oldTemperature = self.temperature
            self.temperature = 30 +5 * math.sin(time/5)
            if self.temperature < 20:

                self.oldTemperature = self.temperature
                self.temperature = 20
            elif self.temperature > 40:
                self.oldTemperature = self.temperature
                self.temperature = 40
            if self.temperature > self.oldTemperature:
                self.state = "heat"
            else:
                self.state = "cool"
            return self


class HeatedSeats:
    def __init__(self):
        self.time = 0
        self.heatedSeats = [HeatedSeat("heat", 30), HeatedSeat("heat", 30), HeatedSeat("heat", 30)]

    def change_temperature(self, time):
        for i in range (0,3):
            self.heatedSeats[i] = self.heatedSeats[i].change_temperature(time)
        return self
    
    def get_info(self, time):
        self = self.change_temperature(time)
        return {
            "HeatedSeat1" : {
            "State" : self.heatedSeats[0].state,
            "Temperature" : int(self.heatedSeats[0].temperature),
            },
            "HeatedSeat2" : {
                "State" : self.heatedSeats[1].state,
                "Temperature" : int(self.heatedSeats[1].temperature),
            },
            "HeatedSeat3" : {
                "State" : self.heatedSeats[2].state,
                "Temperature" : int(self.heatedSeats[2].temperature),
            }
        }
    
    def get_name(self):
        return "HeatSeats"
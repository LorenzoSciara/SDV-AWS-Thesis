class Seat:
    def __init__(self, state, triggered, active, seatbeltFastened, passengerPresent):
        self.state = state #safe/danger
        self.triggered = triggered #bool
        self.active = active #bool
        self.seatbeltFastened = seatbeltFastened #bool
        self.passengerPresent = passengerPresent #bool

    def check_state(self, time):
        if time > 5:
            self.seatbeltFastened = True
        
        if self.passengerPresent:
            if self.seatbeltFastened and self.active:
                self.state = "safe"
            else:
                self.state = "danger"
        else:
            self.state = "safe"
        return self
    


class Airbag:
    def __init__(self):
        self.time = 0
        self.seats = [Seat("safe", False, True, True, True), Seat("danger", False, True, False, True), Seat("safe", False, True, False, False), Seat("safe", False, True, False, False), Seat("danger", False, False, True, True)]

    def check_state(self, time):
        for i in range(0, 5):
            self.seats[i] = self.seats[i].check_state(time)
        return self
    
    def get_info(self, time):
        self.check_state(time)
        return {
            "Seat1" : {
                "State" : self.seats[0].state,
                "Triggered" : self.seats[0].triggered,
                "Active" : self.seats[0].active,
                "SeatbeltFastened" : self.seats[0].seatbeltFastened,
                "PassengerPresent" : self.seats[0].passengerPresent
            },
            "Seat2" : {
                "State" : self.seats[1].state,
                "Triggered" : self.seats[1].triggered,
                "Active" : self.seats[1].active,
                "SeatbeltFastened" : self.seats[1].seatbeltFastened,
                "PassengerPresent" : self.seats[1].passengerPresent
            },
            "Seat3" : {
                "State" : self.seats[2].state,
                "Triggered" : self.seats[2].triggered,
                "Active" : self.seats[2].active,
                "SeatbeltFastened" : self.seats[2].seatbeltFastened,
                "PassengerPresent" : self.seats[2].passengerPresent
            },
            "Seat4" : {
                "State" : self.seats[3].state,
                "Triggered" : self.seats[3].triggered,
                "Active" : self.seats[3].active,
                "SeatbeltFastened" : self.seats[3].seatbeltFastened,
                "PassengerPresent" : self.seats[3].passengerPresent
            },
            "Seat5" : {
                "State" : self.seats[4].state,
                "Triggered" : self.seats[4].triggered,
                "Active" : self.seats[4].active,
                "SeatbeltFastened" : self.seats[4].seatbeltFastened,
                "PassengerPresent" : self.seats[4].passengerPresent
            },
        }
    
    def get_name(self):
        return "Airbag"
        
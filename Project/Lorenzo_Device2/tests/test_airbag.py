from .. import Airbag

def test_airbag_check_state():
    airbag_system = Airbag()
    time = 10
    airbag_system.check_state(time)

    assert airbag_system.seats[0].state == "safe"
    assert airbag_system.seats[1].state == "safe"

def test_airbag_get_info():
    airbag_system = Airbag()
    info = airbag_system.get_info(15)
    expected_info = {
            "Seat1" : {
                "State" : airbag_system.seats[0].state,
                "Triggered" : airbag_system.seats[0].triggered,
                "Active" : airbag_system.seats[0].active,
                "SeatbeltFastened" : airbag_system.seats[0].seatbeltFastened,
                "PassengerPresent" : airbag_system.seats[0].passengerPresent
            },
            "Seat2" : {
                "State" : airbag_system.seats[1].state,
                "Triggered" : airbag_system.seats[1].triggered,
                "Active" : airbag_system.seats[1].active,
                "SeatbeltFastened" : airbag_system.seats[1].seatbeltFastened,
                "PassengerPresent" : airbag_system.seats[1].passengerPresent
            },
            "Seat3" : {
                "State" : airbag_system.seats[2].state,
                "Triggered" : airbag_system.seats[2].triggered,
                "Active" : airbag_system.seats[2].active,
                "SeatbeltFastened" : airbag_system.seats[2].seatbeltFastened,
                "PassengerPresent" : airbag_system.seats[2].passengerPresent
            },
            "Seat4" : {
                "State" : airbag_system.seats[3].state,
                "Triggered" : airbag_system.seats[3].triggered,
                "Active" : airbag_system.seats[3].active,
                "SeatbeltFastened" : airbag_system.seats[3].seatbeltFastened,
                "PassengerPresent" : airbag_system.seats[3].passengerPresent
            },
            "Seat5" : {
                "State" : airbag_system.seats[4].state,
                "Triggered" : airbag_system.seats[4].triggered,
                "Active" : airbag_system.seats[4].active,
                "SeatbeltFastened" : airbag_system.seats[4].seatbeltFastened,
                "PassengerPresent" : airbag_system.seats[4].passengerPresent
            },
        }
    assert info == expected_info

def test_airbag_get_name():
    airbag_system = Airbag()
    assert airbag_system.get_name() == "Airbag"

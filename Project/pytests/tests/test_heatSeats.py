from Lorenzo_Device2 import HeatedSeats

def test_change_temperature():
    heated_seats = HeatedSeats()
    heated_seats.change_temperature(5)
    assert heated_seats.heatedSeats[0].temperature != 30
    assert heated_seats.heatedSeats[1].temperature != 30
    assert heated_seats.heatedSeats[2].temperature != 30


def test_get_info():
    heated_seats = HeatedSeats()
    info = heated_seats.get_info(15)
    assert info["HeatedSeat1"]["State"] == heated_seats.heatedSeats[0].state
    assert info["HeatedSeat1"]["Temperature"] == int(heated_seats.heatedSeats[0].temperature)

def test_get_name():
    heated_seats = HeatedSeats()
    assert heated_seats.get_name() == "HeatSeats"

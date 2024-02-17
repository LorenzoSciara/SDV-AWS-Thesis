from Lorenzo_Device2 import AirConditioning

def test_auto_change_temperature():
    air_conditioner = AirConditioning()
    air_conditioner.auto_change_temperature(5)
    assert air_conditioner.zones[0].temperature != 18
    assert air_conditioner.zones[1].temperature != 20
    assert air_conditioner.zones[2].temperature != 20

def test_auto_change_humidity():
    air_conditioner = AirConditioning()
    air_conditioner.auto_change_humidity(10)
    assert air_conditioner.zones[0].humidity != 30
    assert air_conditioner.zones[1].humidity != 30
    assert air_conditioner.zones[2].humidity != 30

def test_get_info():
    air_conditioner = AirConditioning()
    info = air_conditioner.get_info(15)

    expected_info = {
        "Zone1" : {
        "State" : air_conditioner.zones[0].state,
        "Temperature" : int(air_conditioner.zones[0].temperature),
        "Humidity" : air_conditioner.zones[0].humidity
        },
        "Zone2" : {
            "State" : air_conditioner.zones[1].state,
            "Temperature" : int(air_conditioner.zones[1].temperature),
            "Humidity" : air_conditioner.zones[1].humidity
        },
        "Zone3" : {
            "State" : air_conditioner.zones[2].state,
            "Temperature" : int(air_conditioner.zones[2].temperature),
            "Humidity" : air_conditioner.zones[2].humidity
        }
    }
    assert info == expected_info

def test_get_name():
    air_conditioner = AirConditioning()
    assert air_conditioner.get_name() == "AirConditioning"

from .. import Battery

def test_acellerate():
    battery = Battery()
    battery.acellerate(8)
    assert battery.stateOfCharge != 100
    

def test_decellerate():
    battery = Battery()
    battery.decellerate(12)
    assert battery.stateOfCharge != 0

def test_get_info():
    battery = Battery()
    info = battery.get_info(20)
    assert info["StateOfCharge"] == battery.stateOfCharge
    assert info["BatteryTemperature"] == battery.batteryTemperature
    assert info["EnergyAdded"] == battery.energyAdded

def test_get_name():
    battery = Battery()
    assert battery.get_name() == "Battery"

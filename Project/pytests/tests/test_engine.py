from Lorenzo_Device2 import Engine

def test_acellerate():
    engine = Engine()
    engine.acellerate(8)
    assert engine.acelleratorPedalPosition != 0

def test_decellerate():
    engine = Engine()
    engine.decellerate(12)
    assert engine.acelleratorPedalPosition == 0

def test_get_info():
    engine = Engine()
    info = engine.get_info(20)
    assert info["AcelleratorPedalPosition"] == engine.acelleratorPedalPosition
    assert info["AccelerationEfficiency"] == engine.accelerationEfficiency
    assert info["BrakeRegenerationEfficiency"] == engine.brakeRegenerationEfficiency
    assert info["RPM"] == engine.rpm
    assert info["Gear"] == engine.gear

def test_get_name():
    engine = Engine()
    assert engine.get_name() == "Engine"

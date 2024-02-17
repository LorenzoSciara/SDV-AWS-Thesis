#ifndef ABS_H
#define ABS_H

#include <vector>
#include <iostream>
#include <map>
#include <cmath>

class Wheel {
public:
    int speed;
    int pressure;
    int fluidTemperature;
    int diskTemperature;

    Wheel(int initialSpeed, int initialPressure);
    Wheel& increase_wheel_speed(int time);
    Wheel& decrease_wheel_speed(int time);
};

class ABS {
public:
    std::vector<Wheel> wheels;
    int brakePedalPressure;
    int brakeActualPressure;
    bool tractionControl;

    ABS();
    ABS& change_wheels_speed(int time);
    ABS& change_brake_pedal_pressure(int time);
    std::map<std::string, std::any> get_info(int time);
    std::string get_name();
};

#endif

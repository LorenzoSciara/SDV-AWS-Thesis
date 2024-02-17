#include <iostream>
#include <cmath>
#include <vector>
#include <map>
#include "ABS.h"

Wheel::Wheel(int initialSpeed, int initialPressure) : speed(initialSpeed), pressure(initialPressure), fluidTemperature(10), diskTemperature(30) {}

Wheel& Wheel::increase_wheel_speed(int time) {
    int newSpeed = speed + static_cast<int>(2 * log(time + 1));
    if (newSpeed < 140) {
        speed = newSpeed;
    } else {
        speed = 140;
    }
    fluidTemperature = fluidTemperature - static_cast<int>(log(time + 1));
    fluidTemperature = (fluidTemperature > 0) ? fluidTemperature : 0;
    diskTemperature = diskTemperature - static_cast<int>(3 * log(time + 1));
    diskTemperature = (diskTemperature > 0) ? diskTemperature : 0;
    return *this;
}

Wheel& Wheel::decrease_wheel_speed(int time) {
    int newSpeed = speed - 3;
    if (newSpeed > 0) {
        speed = newSpeed;
    } else {
        speed = 0;
    }
    fluidTemperature = fluidTemperature + static_cast<int>(2 * log(time + 1));
    fluidTemperature = std::min(fluidTemperature, 40);
    diskTemperature = diskTemperature + static_cast<int>(4 * log(time + 1));
    diskTemperature = std::min(diskTemperature, 200);
    return *this;
}

ABS::ABS() : wheels(4, Wheel(0, 3)), brakePedalPressure(0), brakeActualPressure(0), tractionControl(false) {}

ABS& ABS::change_wheels_speed(int time) {
        if (brakePedalPressure == 0) {
            for (int i = 0; i < 4; ++i) {
                wheels[i].increase_wheel_speed(time);
            }
        } else {
            for (int i = 0; i < 4; ++i) {
                wheels[i].decrease_wheel_speed(time);
            }
        }
        return *this;
    }

ABS& ABS::change_brake_pedal_pressure(int time) {
    if (time != 0 && time % 10 == 0) {
        brakePedalPressure = 10;
        brakeActualPressure = 100;
    } else if (time % 5 == 0) {
        brakePedalPressure = 0;
        brakeActualPressure = 0;
    }
    return *this;
}

std::map<std::string, std::any> get_info(int time) {
    tractionControl = false;
    change_wheels_speed(time);
    change_brake_pedal_pressure(time);

    std::map<std::string, std::any> info;
    info["BrakePedalPressure"] = brakePedalPressure;
    info["BrakeActualPressure"] = brakeActualPressure;
    info["TractionControl"] = tractionControl;

    for (int i = 0; i < 4; ++i) {
        std::map<std::string, std::any> wheelInfo;
        wheelInfo["Speed"] = static_cast<int>(wheels[i].speed);
        wheelInfo["Pressure"] = wheels[i].pressure;
        wheelInfo["FluidTemperature"] = wheels[i].fluidTemperature;
        wheelInfo["DiskTemperature"] = wheels[i].diskTemperature;

        info["Wheel" + std::to_string(i + 1)] = wheelInfo;
    }

    return info;
}

std::string ABS::get_name() {
        return "ABS";
}
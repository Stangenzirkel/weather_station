import random
from w1thermsensor import W1ThermSensor

sensor = W1ThermSensor()


def temp(sensor):
    temperature = sensor.get_temperature()
    return temperature


if __name__ == "__main__":
    print(temp())

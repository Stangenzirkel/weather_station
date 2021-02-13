import random


try:
    from w1thermsensor import W1ThermSensor
    sensor = W1ThermSensor()

except Exception:
    sensor = None


def temp(sensor):
    try:
        temperature = sensor.get_temperature()
        return temperature

    except Exception:
        return random.randint(-50, -30)


if __name__ == "__main__":
    print(temp(sensor))

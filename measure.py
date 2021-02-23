import time

try:
    import dht11
    import RPi.GPIO as GPIO

    temp_sensor = 4
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

except Exception:
    print("exception when loading modules")


def sensor_measure():
    tmp = 0
    hmd = 0
    prs = 0

    try:
        result = dht11.DHT11(pin=temp_sensor).read()

        if result.is_valid():
            tmp = result.temperature
            hmd = result.humidity

    except Exception:
        print("exception when measure tmp and hmd")

    finally:
        return tmp, hmd, prs


if __name__ == "__main__":
    print(sensor_measure())

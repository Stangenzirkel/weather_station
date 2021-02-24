import time

try:
    import dht11
    import RPi.GPIO as GPIO
    import time
    from BMP180 import BMP180

    from w1thermsensor import W1ThermSensor
    sensor = W1ThermSensor()

    hmd_sensor = 14
    bmp = BMP180()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

except Exception:
    print("exception when loading modules")

ERROR_CODE = 999


def sensor_measure():
    tmp = ERROR_CODE
    hmd = ERROR_CODE
    prs = ERROR_CODE

    try:
        tmp = round(sensor.get_temperature(), 1)
        result = dht11.DHT11(pin=hmd_sensor).read()
        if result.is_valid():
            hmd = result.humidity

        prs = round(bmp.read_pressure() / 100, 1)

    except Exception:
        print("exception when measure")

    finally:
        return tmp, hmd, prs


if __name__ == "__main__":
    print(sensor_measure())

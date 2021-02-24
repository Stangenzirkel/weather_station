import time

try:
    import dht11
    import RPi.GPIO as GPIO
    import time
    from BMP180 import BMP180

    temp_sensor = 14
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
        result = dht11.DHT11(pin=temp_sensor).read()

        if result.is_valid():
            tmp = result.temperature
            hmd = result.humidity

        prs = round(bmp.read_pressure() / 100, 1)

    except Exception:
        print("exception when measure")

    finally:
        return tmp, hmd, prs


if __name__ == "__main__":
    print(sensor_measure())

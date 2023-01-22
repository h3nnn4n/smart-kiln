from datetime import datetime

import serial

import config
from config import BAUDRATE, PORT, TIMEOUT
from metrics import push_measurement


def loop():
    conn = serial.Serial(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT)
    print(f"connected to port {conn.name}")

    last_read_id = None
    measurements_taken = 0

    while measurements_taken < config.RESET_AFTER_N_MEASUREMENTS:
        data = conn.readline().strip().decode()

        if not data:
            continue

        tokens = data.split(",")
        read_id, *temperatures = tokens

        if read_id == last_read_id:
            continue
        if len(temperatures) == 0:
            continue

        measurements_taken += 1
        last_read_id = read_id

        now = datetime.now()
        now_str = now.strftime("%H:%M:%S")
        print(f"{now_str} {measurements_taken:2}/{config.RESET_AFTER_N_MEASUREMENTS:2} {read_id} {temperatures}")

        for sensor_id, temperature in enumerate(temperatures):
            push_measurement(
                "temperature",
                value=float(temperature),
                tags={
                    "sensor_id": sensor_id,
                },
            )

    if measurements_taken >= config.RESET_AFTER_N_MEASUREMENTS:
        print(f"took {measurements_taken} measurements. Limit is {config.RESET_AFTER_N_MEASUREMENTS}")

    conn.close()


def main():
    while True:
        loop()


if __name__ == "__main__":
    main()

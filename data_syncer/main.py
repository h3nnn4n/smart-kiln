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
    last_read = datetime.now()

    temp_history = {}

    while measurements_taken < config.RESET_AFTER_N_MEASUREMENTS:
        data = conn.readline().strip().decode()

        if not data:
            continue

        tokens = data.split(",")
        read_id, *temperatures = tokens

        now = datetime.now()
        time_since_last_read = (now - last_read).total_seconds()
        push_measurement("time_since_last_read", value=time_since_last_read)

        if read_id == last_read_id:
            continue
        if len(temperatures) == 0:
            continue

        measurements_taken += 1
        last_read_id = read_id
        last_read = now

        now_str = now.strftime("%H:%M:%S")
        print(f"{now_str} {measurements_taken:2}/{config.RESET_AFTER_N_MEASUREMENTS:2} {read_id:2} {temperatures} {time_since_last_read}s")

        for sensor_id, temperature in enumerate(temperatures):
            temperature = float(temperature)
            if sensor_id not in temp_history:
                temp_history[sensor_id] = temperature
            else:
                delta_temp = abs(temperature - temp_history[sensor_id])
                if delta_temp > config.MAX_TEMP_CHANGE:
                    print(f"WARN: temp changed {delta_temp}c in {time_since_last_read}s (from {temp_history[sensor_id]}c to {temperature}c  SKIPPING")
                    continue

            push_measurement(
                "temperature",
                value=temperature,
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

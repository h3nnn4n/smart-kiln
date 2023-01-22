from datetime import datetime

import serial

from config import BAUDRATE, PORT, TIMEOUT

from metrics import push_measurement


def main():
    conn = serial.Serial(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT)
    print(f"connected to port {conn.name}")

    last_read_id = None

    while True:
        data = conn.readline().strip().decode()

        if not data:
            continue

        tokens = data.split(",")
        read_id, *temperatures = tokens

        if read_id == last_read_id:
            continue
        last_read_id = read_id

        now = datetime.now()
        now_str = now.strftime("%H:%M:%S")
        print(f"{now_str} {read_id} {temperatures}")

        for sensor_id, temperature in enumerate(temperatures):
            push_measurement(
                "temperature",
                value=float(temperature),
                tags={
                    "sensor_id": sensor_id,
                },
            )

    conn.close()


if __name__ == "__main__":
    main()

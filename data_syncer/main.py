from datetime import datetime

import serial
from decouple import config

PORT = config("PORT")
BAUDRATE = config("BAUDRATE", default=9600, cast=int)
TIMEOUT = config("TIMEOUT", default=2, cast=int)


def main():
    conn = serial.Serial(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT)
    print(f"connected to port {conn.name}")

    while True:
        data = conn.readline().strip().decode()
        now = datetime.now()
        now_str = now.strftime("%H:%M:%S")
        print(f"{now_str} {data}")

    conn.close()


if __name__ == "__main__":
    main()

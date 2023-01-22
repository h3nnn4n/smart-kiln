import serial
from datetime import datetime

PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
TIMEOUT = 2


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

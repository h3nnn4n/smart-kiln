import typing as t
from datetime import datetime
from os import listdir
from os.path import join
from time import sleep

import serial

import config
from config import BAUDRATE, PORT, TIMEOUT
from metrics import push_measurement


def ping(conn):
    return
    while True:
        conn.writelines(["PING".encode()])
        data = conn.readline().strip().decode()

        if data == "PONG":
            return


def loop(port: t.Optional[str]):
    conn = serial.Serial(
        port=port,
        baudrate=BAUDRATE,
        timeout=TIMEOUT,
    )

    read_errors = 0
    last_read_id = None
    measurements_taken = 0
    last_read = datetime.now()

    temp_history = {}

    # ping(conn)

    while measurements_taken < config.RESET_AFTER_N_MEASUREMENTS:
        now = datetime.now()
        time_since_last_read = (now - last_read).total_seconds()
        time_to_sleep = config.LOOP_UPDATE_INTERVAL - time_since_last_read
        # if time_to_sleep > 0.0:
            # sleep(time_to_sleep)

        data = conn.readline().strip().decode()

        if not data:
            continue

        print(data)

    conn.close()


def find_port() -> str:
    dev_dir = "/dev/"
    all_dev_files = [join(dev_dir, f) for f in listdir(dev_dir)]
    usb_devs = [f for f in all_dev_files if "ttyUSB" in f]

    match len(usb_devs):
        case 0:
            return PORT
        case 1:
            return usb_devs[0]
        case _:
            return usb_devs[0]


def main():
    port = find_port()
    while True:
        loop(port=port)


if __name__ == "__main__":
    main()

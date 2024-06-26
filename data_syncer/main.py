import typing as t
from datetime import datetime
from os import listdir
from os.path import join
from time import sleep

import serial

import config
from config import BAUDRATE, PORT, TIMEOUT
from metrics import push_measurement
from state import State


def ping(conn):
    while True:
        conn.writelines(["PING".encode()])
        data = conn.readline().strip().decode()
        print(data)

        if data == "PONG":
            return


def loop(port: t.Optional[str]):
    conn = serial.Serial(
        port=port,
        baudrate=BAUDRATE,
        timeout=TIMEOUT,
    )

    print(f"connected to port {conn.name}")

    read_errors = 0
    last_read_id = None
    measurements_taken = 0
    last_read = datetime.now()
    state = State(conn)

    ping(conn)

    state.full_sync()

    while measurements_taken < config.RESET_AFTER_N_MEASUREMENTS:
        now = datetime.now()
        time_since_last_read = (now - last_read).total_seconds()
        time_to_sleep = config.LOOP_UPDATE_INTERVAL - time_since_last_read
        if time_to_sleep > 0.0:
            sleep(time_to_sleep)

        state.update()

        conn.writelines(["READ_TEMP".encode()])
        data = conn.readline().strip().decode()

        if not data:
            continue

        tokens = data.split(",")
        read_id, *temperatures = tokens

        now = datetime.now()
        time_since_last_read = (now - last_read).total_seconds()
        push_measurement("time_since_last_read", value=time_since_last_read)

        if read_id == last_read_id or len(temperatures) == 0:
            print(f"read failed {read_errors}/{config.RESET_AFTER_N_ERRORS}")
            read_errors += 1

            if read_errors >= config.RESET_AFTER_N_ERRORS:
                break

            continue

        measurements_taken += 1
        last_read_id = read_id
        last_read = now

        now_str = now.strftime("%H:%M:%S")
        print(
            f"{now_str} {measurements_taken:2}/{config.RESET_AFTER_N_MEASUREMENTS:2} {read_id:2} {temperatures} {time_since_last_read}s"
        )

        for sensor_id, temperature in enumerate(temperatures):
            if temperature == "nan" or float(temperature) >= 1500:
                #print(f"WARN: sensor {sensor_id} is open")
                continue

            temperature = float(temperature)

            push_measurement(
                "temperature",
                value=temperature,
                tags={
                    "sensor_id": sensor_id,
                },
            )

    if measurements_taken >= config.RESET_AFTER_N_MEASUREMENTS:
        print(
            f"took {measurements_taken} measurements. Limit is {config.RESET_AFTER_N_MEASUREMENTS}"
        )

    if read_errors >= config.RESET_AFTER_N_ERRORS:
        print(
            f"Error limit is {config.RESET_AFTER_N_MEASUREMENTS}. Got {read_errors} errors"
        )

    conn.close()


def find_port() -> str:
    dev_dir = "/dev/"
    all_dev_files = [join(dev_dir, f) for f in listdir(dev_dir)]
    usb_devs = [f for f in all_dev_files if "ttyUSB" in f]
    print(f"found {usb_devs=}")

    match len(usb_devs):
        case 0:
            print(f"found no match for ttyUSB, using default {PORT=}")
            return PORT
        case 1:
            return usb_devs[0]
        case _:
            print(f"WARNING found {len(usb_devs)}, picking first one")
            return usb_devs[0]


def main():
    print("Smart Kiln data syncer")
    print("running with:")
    print(f"ASYNC_METRICS={config.ASYNC_METRICS}")
    print(f"STATE_FILE_READ_INTERVAL={config.STATE_FILE_READ_INTERVAL}")
    print(f"LOOP_UPDATE_INTERVAL={config.LOOP_UPDATE_INTERVAL}")
    print(f"PROGRAM_UPDATE_INTERVAL={config.PROGRAM_UPDATE_INTERVAL}")
    print()

    port = find_port()
    while True:
        loop(port=port)


if __name__ == "__main__":
    main()

import pickle
import math
from collections import defaultdict
import typing as t
from datetime import datetime

from metrics import push_measurement
import config


def set_var(conn, key, value):
    conn.writelines([f"SET {key}={value}".encode()])
    data = conn.readline().strip().decode()
    print(data)


class State:
    __pickle_filename: t.Optional[str]

    def __init__(self, conn):
        self.kp = 0.0
        self.kd = 0.0
        self.ki = 0.0

        self.setpoint = 0.0
        self.pid_enabled = 0.0

        self.conn = conn

        self.data_history = defaultdict(list)
        self.__pickle_filename = None

        self.last_state_update = datetime.now()

    def update(self):
        self.delta_sync()
        self.read_pid()

    def delta_sync(self, force=False):
        now = datetime.now()
        time_since_last_update = (now - self.last_state_update).total_seconds()
        if not force and time_since_last_update < config.STATE_FILE_READ_INTERVAL:
            return

        push_measurement(
            "time_since_last_state_update",
            value=time_since_last_update,
            tags={"type": "delta"},
        )
        self.last_state_update = now

        for key, value in self.state.items():
            value = float(value)

            if getattr(self, key) != value:
                setattr(self, key, value)
                set_var(self.conn, key, value)

    def full_sync(self):
        """
        Syncs the full state of the kiln PID controller
        """
        now = datetime.now()
        time_since_last_update = (now - self.last_state_update).total_seconds()
        push_measurement(
            "time_since_last_state_update",
            value=time_since_last_update,
            tags={"type": "full"},
        )
        self.last_state_update = now

        for key, value in self.state.items():
            value = float(value)
            setattr(self, key, value)
            set_var(self.conn, key, value)

        self.read_pid()

    def read_pid(self):
        self.conn.writelines(["READ_PID".encode()])
        data = self.conn.readline().strip().decode()

        if data[:3] != "PID":
            print("WARN: Data received didnt start with PID! got:")
            print(data)
            return

        now = datetime.now()
        self.data_history["time"].append(now)

        tokens = data[4:].split(";")
        for token in tokens:
            key, _, value = token.partition("=")
            value = float(value)

            if math.isnan(value):
                continue

            if key in ["kp", "kd", "ki"]:
                metric_name = "pid_param"
            else:
                metric_name = "pid_state"

            push_measurement(
                metric_name,
                value=value,
                tags={
                    "pid": True,
                    "key": key,
                },
            )
            self.data_history[metric_name].append(value)
            # print(f"{key}={value}")

        self._write_state_to_disk()

    def _write_state_to_disk(self) -> None:
        if not config.STORE_METRICS_LOCALY:
            return

        with open(self._pickle_filename, "wb") as f:
            pickle.dump(self, f)

    @property
    def state(self):
        state = read_state_file()
        state.update(read_temp_file())
        return state

    @property
    def _pickle_filename(self) -> str:
        if not self.__pickle_filename:
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            self.__pickle_filename = f"state_{timestamp}.pickle"

        return self.__pickle_filename


def read_state_file():
    data = {}

    with open("state.txt", "rt") as f:
        for line in f.readlines():
            line = line.strip()
            key, _, value = line.partition("=")
            data[key] = value

    return data


def read_temp_file():
    data = {}

    try:
        with open("temp.txt", "rt") as f:
            for line in f.readlines():
                line = line.strip()
                key, _, value = line.partition("=")
                data[key] = value
    except Exception as e:
        print(f"WARN: Failed to read temp.txt with error {e}")

    return data

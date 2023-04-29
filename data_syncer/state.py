from metrics import push_measurement


def read_pid(conn):
    conn.writelines(["READ_PID".encode()])
    data = conn.readline().strip().decode()

    if data[:3] != "PID":
        print("WARN: Data received didnt start with PID! got:")
        print(data)
        return

    tokens = data[4:].split(";")
    for token in tokens:
        key, _, value = token.partition("=")
        value = float(value)

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
        # print(f"{key}={value}")


def set_var(conn, key, value):
    conn.writelines([f"SET {key}={value}".encode()])
    data = conn.readline().strip().decode()
    print(data)


class State:
    def __init__(self, conn):
        self.kp = 0.0
        self.kd = 0.0
        self.ki = 0.0

        self.setpoint = 0.0

        self.pid_enabled = 0.0

        self.conn = conn

    def update(self):
        self.delta_sync()
        read_pid(self.conn)

    def delta_sync(self):
        for key, value in self.state.items():
            value = float(value)

            if getattr(self, key) != value:
                setattr(self, key, value)
                set_var(self.conn, key, value)

    def full_sync(self):
        """
        Syncs the full state of the kiln PID controller
        """
        for key, value in self.state.items():
            value = float(value)
            setattr(self, key, value)
            set_var(self.conn, key, value)

        read_pid(self.conn)

    @property
    def state(self):
        state = read_state_file()
        state.update(read_temp_file())
        return state


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

from datetime import datetime, timedelta


PROGRAM_UPDATE_INTERVAL = timedelta(seconds=60)


class ProgramState:
    def __init__(self):
        self.start_time = datetime.now()


def main():
    read_program()


def read_program():
    temps = {}

    with open("program.txt", "rt") as f:
        for line in f.readlines():
            line = line.strip()
            timestamp, _, temp = line.partition(" ")
            hour, _, minute = timestamp.partition(":")
            time_offset = timedelta(hours=int(hour), minutes=int(minute))

            temp = int(temp)

            temps[time_offset] = temp

    for k, v in temps.items():
        print(f"{k} {v}")


if __name__ == "__main__":
    main()

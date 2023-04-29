import itertools
from datetime import datetime, timedelta

PROGRAM_UPDATE_INTERVAL = timedelta(seconds=60)

DEBUG = True

if DEBUG:
    import matplotlib.pyplot as plt  # noqa
    import seaborn as sns  # noqa

    sns.set_style("whitegrid")


class ProgramState:
    def __init__(self, program):
        self.program = program

        # These are actual timestamps
        self.start_time = datetime.now()
        self.end_time = self._calculate_end_time()

        # These are timedeltas
        self.program_timer = timedelta(seconds=0)
        self.end_time_offset = self._calculate_end_offset()

        for k, v in self.program.items():
            print(f"{k} {v}")

    def _calculate_end_offset(self):
        return max(list(self.program.keys()))

    def _calculate_end_time(self):
        end_time_offset = self._calculate_end_offset()
        end_time = self.start_time + end_time_offset
        return end_time

    def run(self):
        now = self.start_time
        x = []
        y = []

        while now < self.end_time:
            now += PROGRAM_UPDATE_INTERVAL
            self.program_timer += PROGRAM_UPDATE_INTERVAL
            target_temp = self._calculate_temperature(self.program_timer)
            print(f"{now=} {target_temp=}")

            if DEBUG:
                x.append(now)
                y.append(target_temp)

        if DEBUG:
            sns.lineplot(x=x, y=y)
            sns.despine(trim=True)
            plt.xticks(rotation=20, ha='right')
            plt.savefig("plot.png")

    def _calculate_temperature(self, time: timedelta) -> float:
        for time1, time2 in itertools.pairwise(self.program.keys()):
            if time1 < time and time <= time2:
                break

        temp1 = self.program[time1]
        temp2 = self.program[time2]

        # Simple linear interpolation
        p: float = (time - time1) / (time2 - time1)
        temp: float = temp1 + (temp2 - temp1) * p

        return temp


def main():
    program = read_program()
    program_state = ProgramState(program)
    program_state.run()


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

    return temps


if __name__ == "__main__":
    main()

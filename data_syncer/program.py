#!/usr/bin/env python3

import itertools
import argparse
from datetime import datetime, timedelta

import matplotlib.pyplot as plt  # type:ignore
import seaborn as sns  # type:ignore

PROGRAM_UPDATE_INTERVAL = timedelta(seconds=60)
sns.set_style("whitegrid")


class ProgramState:
    def __init__(self, program: dict[timedelta, int], preview_mode: bool = True):
        self.program = program
        self.preview_mode = preview_mode

        # These are actual timestamps
        self.start_time = datetime.now()
        self.end_time = self._calculate_end_time()

        # These are timedeltas
        self.program_timer = timedelta(seconds=0)
        self.end_time_offset = self._calculate_end_offset()

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

            if not self.preview_mode:
                print(f"{now=} {target_temp=}")

            if self.preview_mode:
                x.append(now)
                y.append(target_temp)

        if self.preview_mode:
            sns.lineplot(x=x, y=y)
            sns.despine(trim=True)
            plt.xticks(rotation=20, ha="right")
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
    parser = argparse.ArgumentParser(
        prog="SmartKiln - Firing Schedule",
        description="Reads a firing schedule and forwards it to the kiln",
    )
    parser.add_argument("filename", help="File with the firing schedule")
    parser.add_argument("-p", "--preview", action="store_true")
    args = parser.parse_args()

    program = read_program(args.filename)
    program_state = ProgramState(program, preview_mode=args.preview)
    program_state.run()


def read_program(filename: str) -> dict[timedelta, int]:
    temps = {}

    print(f"reading from {filename}")
    print("firing schedule:")

    with open(filename, "rt") as f:
        for line in f.readlines():
            line = line.strip()
            timestamp, _, temp = line.partition(" ")
            hour, _, minute = timestamp.partition(":")
            time_offset = timedelta(hours=int(hour), minutes=int(minute))
            temps[time_offset] = int(temp)

            print(f"{timestamp} {temp}")

    print()
    print(f"firing schedule has {len(temps)} steps")

    return temps


if __name__ == "__main__":
    main()

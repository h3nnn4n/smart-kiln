#!/usr/bin/env python3

import argparse
import itertools
import pickle
import sys
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import matplotlib.pyplot as plt  # type:ignore
import seaborn as sns  # type:ignore

import config


sns.set_style("whitegrid")


class ProgramState:
    def __init__(self, program: dict[timedelta, int], preview_mode: bool = True):
        self.program = program
        self.preview_mode = preview_mode

        # These are actual timestamps
        self.now = datetime.now()
        self.start_time = self.now
        self.end_time = self._calculate_end_time()

        # These are timedeltas
        self.program_timer = timedelta(seconds=0)
        self.end_time_offset = self._calculate_end_offset()

        self.x: list[datetime] = []
        self.y: list[float] = []

    def _update_timer(self):
        """
        If in preview_mode, `now` and `program_timer` are increased by
        `program_update_interval` and the function returns immediately.

        Otherwise, the function waits the time set in
        `program_update_interval`, then updates `now` and `program_timer` and
        returns.

        The first time this function is called, it never sleeps. This ensures
        that we set the temperature straightway, instead of waiting for a full
        timestep before doing it.
        """
        first_update = self.start_time == self.now

        if not self.preview_mode and not first_update:
            sleep(self.program_update_interval.total_seconds())

        now = datetime.now()
        timestep = now - self.now
        self.now = now
        self.program_timer += timestep

    @property
    def program_update_interval(self) -> timedelta:
        return timedelta(seconds=config.PROGRAM_UPDATE_INTERVAL)

    def update(self) -> bool:
        """
        Steps the firing schedule. Blocks until the next update. Returns
        `False` when the program completes and `True` while the program still
        running.
        """
        done = self.now > self.end_time
        if done:
            if self.preview_mode:
                self._save_plot()
            return False

        self._update_timer()

        target_temp = self._calculate_temperature(self.program_timer)

        if not self.preview_mode:
            self._write_setpoint(target_temp)
            print(f"{self.now} {target_temp:6.2f}c")

        if self.preview_mode:
            self.x.append(self.now)
            self.y.append(target_temp)

        return True

    def _save_plot(self) -> None:
        sns.lineplot(x=self.x, y=self.y)
        sns.despine(trim=True)
        plt.xticks(rotation=20, ha="right")
        plt.savefig("plot.png")

    def _calculate_end_offset(self):
        return max(list(self.program.keys()))

    def _calculate_end_time(self):
        end_time_offset = self._calculate_end_offset()
        end_time = self.start_time + end_time_offset
        return end_time

    def _write_setpoint(self, temperature: float) -> None:
        with open("setpoint.txt", "wt") as f:
            f.write(f"setpoint={temperature}\n")
            f.write("pid_enabled=1.0\n")

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
    parser.add_argument("filepath", help="File with the firing schedule")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    conflicting_args = [args.preview, args.start, args.resume]
    if sum(conflicting_args) > 1:
        print("conflicting args")
        sys.exit(1)

    if sum(conflicting_args) == 0:
        print("please set an action, eg --start")
        sys.exit(1)

    program_name = get_program_name(args.filepath)

    if args.start or args.preview:
        program = read_program(args.filepath)
        program_state = ProgramState(
            program=program,
            preview_mode=args.preview,
        )

        if args.start:
            store_state(program_state, program_name)

    if args.resume:
        program_state = read_state(program_name)

    while program_state.update():
        if not args.preview:
            store_state(program_state, program_name)


def store_state(program: ProgramState, program_name: str) -> None:
    program_state_filepath = f"{program_name}.pickle"
    with open(program_state_filepath, "wb") as f:
        pickle.dump(program, f, pickle.HIGHEST_PROTOCOL)


def read_state(program_name: str) -> ProgramState:
    program_state_filepath = f"{program_name}.pickle"
    with open(program_state_filepath, "rb") as f:
        return pickle.load(f)


def get_program_name(filepath: str) -> str:
    filename = Path(filepath).name
    program_name, _, _ = filename.partition(".")
    return program_name


def read_program(filepath: str) -> dict[timedelta, int]:
    temps = {}

    print(f"firing schedule {get_program_name(filepath)}")
    print(f"reading from {filepath}")
    print("firing schedule:")

    with open(filepath, "rt") as f:
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

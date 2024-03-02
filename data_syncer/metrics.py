import json
from datetime import datetime, timezone
from os import path
from queue import Empty, SimpleQueue
from threading import Thread

from influxdb import InfluxDBClient

import config


INFLUX_CLIENT = None

QUEUE = SimpleQueue()
LAST_INFLUX_BATCH_PUSH = datetime.now()


def push_measurement(name: str, value, tags=None):
    data = _build_measurement(name=name, value=value, tags=tags)

    push(data)


def push(data):
    if not isinstance(data, list):
        data = [data]

    _ensure_timestamp(data)

    if config.ASYNC_METRICS:
        Thread(target=_push, args=(data,)).start()
    else:
        _push(data)


def _build_measurement(name: str, value, tags=None) -> dict:
    if tags is None:
        tags = {}

    data = {
        "measurement": name,
        "fields": {
            "value": value,
        },
        "tags": tags,
    }

    _ensure_timestamp(data)

    return data


def sync_data_to_influx():
    if not config.INFLUXDB_BATCH_WRITES:
        print("[WARN] sync_data_to_influx called but INFLUXDB_BATCH_WRITES is not set")
        return

    payload = []

    while not QUEUE.empty():
        item = QUEUE.get()
        payload.append(item)

    if len(payload) == 0:
        return

    batch_size_measurement = _build_measurement(name="metrics_batch_size", value=len(payload))
    payload.append(batch_size_measurement)
    _write_to_influx(payload)


def _push(data: list[dict]) -> None:
    _push_to_disk(data)
    _push_to_influx(data)


def _push_to_disk(data: list[dict]) -> None:
    if not config.LOCAL_DB_ENABLE:
        return

    try:
        now = datetime.utcnow()
        now = now.replace(second=0, microsecond=0)
        now = now.replace(minute=(now.minute // 10) * 10)

        filename = f"metrics_{now.strftime('%Y%m%d_%H%M')}.jsonl"
        filepath = path.join("metrics_db", filename)

        with open(filepath, "a+") as f:
            f.write(json.dumps(data))
            f.write("\n")

    except Exception as e:
        if config.LOCAL_DB_IGNORE_ERRORS:
            print(f"WARN: Failed to write {len(data)} data points to local db with error {e}")
            return

        raise


def _push_to_influx(data: list[dict]) -> None:
    global LAST_INFLUX_BATCH_PUSH

    if config.INFLUXDB_BATCH_WRITES:
        for item in data:
            QUEUE.put(item)

        now = datetime.now()
        if (now - LAST_INFLUX_BATCH_PUSH).total_seconds() > config.INFLUXDB_BATCH_INTERVAL:
            LAST_INFLUX_BATCH_PUSH = now
            sync_data_to_influx()
    else:
        _write_to_influx(data)


def _write_to_influx(data: list[dict]) -> None:
    try:
        client = _influxdb()
        client.write_points(data)
    except Exception as e:
        if config.INFLUXDB_IGNORE_ERRORS:
            print(f"WARN: Failed to push {len(data)} data points to influxdb with error {e}")
            return

        raise


def _ensure_timestamp(data):
    if isinstance(data, list):
        for d in data:
            _ensure_timestamp(d)

        return

    if data.get("time"):
        return

    data["time"] = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()


def _influxdb():
    global INFLUX_CLIENT

    if not INFLUX_CLIENT:
        INFLUXDB_CLIENT = InfluxDBClient(
            config.INFLUXDB_HOST,
            config.INFLUXDB_PORT,
            config.INFLUXDB_USER,
            config.INFLUXDB_PASSWORD,
            config.INFLUXDB_DATABASE,
            ssl=False,
            verify_ssl=False,
        )

    return INFLUXDB_CLIENT

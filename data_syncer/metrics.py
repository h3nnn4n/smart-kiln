from datetime import datetime, timezone
from threading import Thread

from influxdb import InfluxDBClient

import config


def push_measurement(name, value, tags=None):
    if tags is None:
        tags = {}

    data = {
        "measurement": name,
        "fields": {
            "value": value,
        },
        "tags": tags,
    }

    push(data)


def push(data):
    if not isinstance(data, list):
        data = [data]

    _ensure_timestamp(data)

    if config.ASYNC_METRICS:
        Thread(target=_push, args=(data,)).start()
    else:
        _push(data)


def _push(data):
    client = _influxdb()
    client.write_points(data)


def _ensure_timestamp(data):
    if isinstance(data, list):
        for d in data:
            _ensure_timestamp(d)

        return

    if data.get("time"):
        return

    data["time"] = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()


def _influxdb():
    return InfluxDBClient(
        config.INFLUXDB_HOST,
        config.INFLUXDB_PORT,
        config.INFLUXDB_USER,
        config.INFLUXDB_PASSWORD,
        config.INFLUXDB_DATABASE,
        ssl=False,
        verify_ssl=False,
    )

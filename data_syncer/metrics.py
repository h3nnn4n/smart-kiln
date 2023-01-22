from datetime import datetime

import config
from influxdb import InfluxDBClient


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

    data["time"] = datetime.now().isoformat()


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

from decouple import config


PORT = config("PORT")
BAUDRATE = config("BAUDRATE", default=115200, cast=int)
TIMEOUT = config("TIMEOUT", default=2, cast=int)

RESET_AFTER_N_MEASUREMENTS = config("RESET_AFTER_N_MEASUREMENTS", default=600, cast=int)
RESET_AFTER_N_ERRORS = config("RESET_AFTER_N_ERRORS", default=5, cast=int)

MAX_TEMP_CHANGE = config("MAX_TEMP_CHANGE", default=100, cast=int)

INFLUXDB_HOST = config("INFLUXDB_HOST")
INFLUXDB_PORT = config("INFLUXDB_PORT")
INFLUXDB_USER = config("INFLUXDB_USER")
INFLUXDB_PASSWORD = config("INFLUXDB_PASSWORD")
INFLUXDB_DATABASE = config("INFLUXDB_DATABASE")
INFLUXDB_IGNORE_ERRORS = config("INFLUXDB_IGNORE_ERRORS", default=True, cast=bool)

# If true, calls to push to influx will be grouped together and set on a single
# api call. May delay data delivery for a few seconds.
INFLUXDB_BATCH_WRITES = config("INFLUXDB_BATCH_WRITES", default=True, cast=bool)
# The minimum amount of time to wait before flushing the batched data
INFLUXDB_BATCH_INTERVAL = config("INFLUXDB_BATCH_INTERVAL", default=2.0, cast=float)

LOCAL_DB_ENABLE = config("LOCAL_DB_ENABLE", default=True, cast=bool)
LOCAL_DB_IGNORE_ERRORS = config("LOCAL_DB_IGNORE_ERRORS", default=True, cast=bool)

ASYNC_METRICS = config("ASYNC_METRICS", default=True, cast=bool)
STORE_METRICS_LOCALY = config("STORE_METRICS_LOCALY", default=False, cast=bool)

# The interval between each temp update from the firing schedule program
PROGRAM_UPDATE_INTERVAL = config("PROGRAM_UPDATE_INTERVAL", default=60, cast=int)

# The interval between each state sync with the arduino board
LOOP_UPDATE_INTERVAL = config("LOOP_UPDATE_INTERVAL", default=1, cast=float)

# The minimum interval between state.txt reads from disk
STATE_FILE_READ_INTERVAL = config("STATE_FILE_READ_INTERVAL", default=1, cast=float)

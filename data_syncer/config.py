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

LOCAL_DB_ENABLE = config("LOCAL_DB_ENABLE", default=True, cast=bool)
LOCAL_DB_IGNORE_ERRORS = config("LOCAL_DB_IGNORE_ERRORS", default=True, cast=bool)

ASYNC_METRICS = config("ASYNC_METRICS", default=True, cast=bool)

# The interval between each temp update from the firing schedule program
PROGRAM_UPDATE_INTERVAL = config("PROGRAM_UPDATE_INTERVAL", default=60, cast=int)

# The interval between each state sync with the arduino board
LOOP_UPDATE_INTERVAL = config("LOOP_UPDATE_INTERVAL", default=1, cast=float)

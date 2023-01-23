from decouple import config


PORT = config("PORT")
BAUDRATE = config("BAUDRATE", default=9600, cast=int)
TIMEOUT = config("TIMEOUT", default=2, cast=int)

RESET_AFTER_N_MEASUREMENTS = config("RESET_AFTER_N_MEASUREMENTS", default=30, cast=int)

MAX_TEMP_CHANGE = config("MAX_TEMP_CHANGE", default=25, cast=int)

INFLUXDB_HOST = config("INFLUXDB_HOST")
INFLUXDB_PORT = config("INFLUXDB_PORT")
INFLUXDB_USER = config("INFLUXDB_USER")
INFLUXDB_PASSWORD = config("INFLUXDB_PASSWORD")
INFLUXDB_DATABASE = config("INFLUXDB_DATABASE")

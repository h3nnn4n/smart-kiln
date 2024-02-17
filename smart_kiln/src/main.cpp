#include <Arduino.h>
#include <EEPROM.h>
#include <Wire.h>

#include "max31855.h"
#include "max6675.h"
#include "pid.h"

const int common_CLK = 4;
const int common_DO  = 5;

const int sensor1_CS = 6;
const int sensor2_CS = 7;
const int sensor3_CS = 8;
const int sensor4_CS = 9;

const int sensor4_DO = 13;

// The Solid State Relay pin
const int SSR = 3;

unsigned int counter = 0;

double pid_input;
double pid_output;
double pid_setpoint = 0.0f;
double pid_kp;
double pid_ki;
double pid_kd;

bool pid_enabled = false;

float t1 = 0;
float t2 = 0;
float t3 = 0;
float t4 = 0;

unsigned int PID_KP_ADDR = 0;
unsigned int PID_KI_ADDR = 4;
unsigned int PID_KD_ADDR = 8;


PID pid(&pid_input, &pid_output, &pid_setpoint, pid_kp, pid_ki, pid_kd, 0);

MAX6675 sensor1(common_CLK, sensor1_CS, common_DO);
MAX6675 sensor2(common_CLK, sensor2_CS, common_DO);
MAX6675 sensor3(common_CLK, sensor3_CS, common_DO);
MAX31855 sensor4(common_CLK, sensor4_CS, sensor4_DO);

void setup() {
    Serial.begin(115200);
	Serial.setTimeout(10);

    pinMode(SSR, OUTPUT);
	analogWrite(SSR, 0);

	pid.SetMode(pid_enabled);
	pid.SetOutputLimits(0.0, 255.0);

	EEPROM.get(PID_KP_ADDR, pid_kp);
	EEPROM.get(PID_KI_ADDR, pid_ki);
	EEPROM.get(PID_KD_ADDR, pid_kd);

    delay(500);

    Serial.println("BEGIN");
}

void log_pid_data() {
	Serial.print("PID:");
	Serial.print("enabled=");
	Serial.print(int(pid_enabled));
	Serial.print(";input=");
	Serial.print(pid_input);
	Serial.print(";output=");
	Serial.print(pid_output);
	Serial.print(";setpoint=");
	Serial.print(pid_setpoint);
	Serial.print(";kp=");
	Serial.print(pid_kp);
	Serial.print(";kd=");
	Serial.print(pid_kd);
	Serial.print(";ki=");
	Serial.print(pid_ki);
	Serial.println();
}

void read_pid_temp() {
	t1 = sensor1.readCelsius();
	pid_input = t1;
}

void pid_loop() {
	read_pid_temp();

	if (pid.Compute()) {
		analogWrite(SSR, pid_output);
	}
}

void log_temps() {
	t1 = sensor1.readCelsius();
	t2 = sensor2.readCelsius();
	t3 = sensor3.readCelsius();

	// The first read, after reading from the max6675 sensor always comes out
	// with the wrong temps. Reading it twice is a workaround for now until the
	// rootcause is fixed.
	sensor4.readCelsius();
	t4 = sensor4.readCelsius();

	Serial.print(counter);
	Serial.print(",");
	Serial.print(t1);
	Serial.print(",");
	Serial.print(t2);
	Serial.print(",");
	Serial.print(t3);
	Serial.print(",");
	Serial.print(t4);
	Serial.println();

	counter++;
}

void set_cmd(String cmd) {
	int separator_index = cmd.indexOf("=");
	String key = cmd.substring(0, separator_index);
	String value_str = cmd.substring(separator_index + 1);
	float value = value_str.toFloat();

	if (key == "setpoint") {
		pid_setpoint = value;
	} else if (key == "kp") {
		pid_kp = value;
		EEPROM.put(PID_KP_ADDR, pid_kp);
		pid.SetTunings(pid_kp, pid_ki, pid_kd);
	} else if (key == "kd") {
		pid_kd = value;
		EEPROM.put(PID_KD_ADDR, pid_kd);
		pid.SetTunings(pid_kp, pid_ki, pid_kd);
	} else if (key == "ki") {
		pid_ki = value;
		EEPROM.put(PID_KI_ADDR, pid_ki);
		pid.SetTunings(pid_kp, pid_ki, pid_kd);
	} else if (key == "pid_enabled") {
		pid_enabled = value;
		pid.SetMode(pid_enabled);
		pid_enabled = pid.GetMode();

		if (!pid_enabled) {
			analogWrite(SSR, 0);
		}
	}

	Serial.print("SET ");
	Serial.print(key);
	Serial.print("=");
	Serial.print(value);
	Serial.println();
}

void read_serial() {
	if (!Serial.available()) return;
	String cmd = Serial.readString();
	cmd.trim();

	if (cmd == "READ_PID") {
		log_pid_data();
	} else if (cmd == "READ_TEMP") {
		log_temps();
	} else if (cmd == "PING") {
		Serial.println("PONG");
	} else if (cmd.startsWith("SET ")) {
		set_cmd(cmd.substring(4));
	}
}

void loop() {
	pid_loop();

	read_serial();
}

#include <Arduino.h>
#include <Wire.h>

#include "max6675.h"
#include "pid.h"

const int common_CLK = 4;
const int common_DO  = 5;

const int sensor1_CS = 6;
const int sensor2_CS = 7;
const int sensor3_CS = 8;
const int sensor4_CS = 9;

// The Solid State Relay pin
const int SSR = 3;

unsigned long now;

// How long we wait before sending the data to the logger
const int SERIAL_OUT_INTERVAL = 1 * 1000;
unsigned long serial_out_timer = 0;

// How long we wait before reading the sensors
const int SENSOR_READ_INTERVAL = 1 * 250;
unsigned long sensor_read_timer = 0;

unsigned int counter = 0;

double pid_input;
double pid_output;
double pid_setpoint = 175.0f;
double pid_kp = 10.0f;
double pid_ki = 0.0f;
double pid_kd = 7.5f;

float t1 = 0;
float t2 = 0;
float t3 = 0;


PID pid(&pid_input, &pid_output, &pid_setpoint, pid_kp, pid_ki, pid_kd, 0);

MAX6675 sensor1(common_CLK, sensor1_CS, common_DO);
MAX6675 sensor2(common_CLK, sensor2_CS, common_DO);
MAX6675 sensor3(common_CLK, sensor3_CS, common_DO);

void setup() {
	serial_out_timer = millis();
	sensor_read_timer = millis();

    Serial.begin(9600);

    Serial.println("Smart kiln init");

    pinMode(SSR, OUTPUT);
    digitalWrite(SSR, LOW);

	pid.SetMode(0);
	pid.SetOutputLimits(0.0, 255.0);

    delay(500);

    digitalWrite(SSR, HIGH);

	now = millis();
}

void log_pid_data() {
	Serial.print("PID:");
	Serial.print(pid_input);
	Serial.print(",");
	Serial.print(pid_output);
	Serial.print(",");
	Serial.print(pid_setpoint);
	Serial.print(",");
	Serial.print(pid_kp);
	Serial.print(",");
	Serial.print(pid_kd);
	Serial.print(",");
	Serial.print(pid_ki);
	Serial.println();
}

void read_pid_temp() {
	if ((now - sensor_read_timer) > SENSOR_READ_INTERVAL) {
		t1 = sensor1.readCelsius();

		pid_input = t1;
		sensor_read_timer = now;
	}
}

void pid_loop() {
	if (pid.Compute()) {
		analogWrite(SSR, pid_output);
	}
}

void log_temps() {
	t1 = sensor1.readCelsius();
	t2 = sensor2.readCelsius();
	t3 = sensor3.readCelsius();

	Serial.print(counter);
	Serial.print(",");
	Serial.print(t1);
	Serial.print(",");
	Serial.print(t2);
	Serial.print(",");
	Serial.print(t3);
	Serial.println();

	counter++;
	serial_out_timer = now;
}

void read_serial() {
	if (!Serial.available()) return;
	String cmd = Serial.readString();

	if (cmd == "READ_PID") {
		log_pid_data();
	} else if (cmd == "READ_TEMP") {
		log_temps();
	}
}

void loop() {
	now = millis();

	read_pid_temp();
	pid_loop();

	read_serial();
}

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

// How long we wait before reading the sensors after each loop
const int LOOP_INTERVAL = 1;  // Seconds

unsigned int counter = 0;

double pid_input;
double pid_output;
double pid_setpoint = 125.0f;
double pid_kp = 7.5f;
double pid_ki = 0.0f;
double pid_kd = 0.0f;

PID pid(&pid_input, &pid_output, &pid_setpoint, pid_kp, pid_ki, pid_kd, 0);

MAX6675 sensor1(common_CLK, sensor1_CS, common_DO);
MAX6675 sensor2(common_CLK, sensor2_CS, common_DO);
MAX6675 sensor3(common_CLK, sensor3_CS, common_DO);

void setup() {
    Serial.begin(9600);

    Serial.println("Smart kiln init");

    pinMode(SSR, OUTPUT);
    digitalWrite(SSR, LOW);

	pid.SetMode(1);  // Enable pid
	pid.SetOutputLimits(0.0, 255.0);

    delay(500);

    digitalWrite(SSR, HIGH);
}

void loop() {
	float t1 = sensor1.readCelsius();
	float t2 = sensor2.readCelsius();
	float t3 = sensor3.readCelsius();

	pid_input = t1;

	if (pid.Compute()) {
		analogWrite(SSR, pid_output);
	}

    Serial.print(counter);
    Serial.print(",");
    Serial.print(t1);
	Serial.print(",");
	Serial.print(pid_input);
	Serial.print(",");
	Serial.print(pid_output);
    Serial.println();

    counter++;
    delay(LOOP_INTERVAL * 1000);
}

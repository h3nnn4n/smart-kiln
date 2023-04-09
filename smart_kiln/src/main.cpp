#include <Arduino.h>
#include <Wire.h>

#include "max6675.h"

const int common_CLK = 4;
const int common_DO = 5;

const int sensor1_CS = 6;
const int sensor2_CS = 7;
const int sensor3_CS = 8;
const int sensor4_CS = 9;

// How long we wait before reading the sensors after each loop
const int LOOP_INTERVAL = 1;  // Seconds

unsigned int counter = 0;

MAX6675 sensor1(common_CLK, sensor1_CS, common_DO);
MAX6675 sensor2(common_CLK, sensor2_CS, common_DO);
MAX6675 sensor3(common_CLK, sensor3_CS, common_DO);
MAX6675 sensor4(common_CLK, sensor4_CS, common_DO);

void setup() {
    Serial.begin(9600);

    Serial.println("Smart kiln init");

    delay(500);
}

void loop() {
    float t1 = sensor1.readCelsius();
    float t2 = sensor2.readCelsius();
    float t3 = sensor3.readCelsius();
    float t4 = sensor4.readCelsius();

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
    delay(LOOP_INTERVAL * 1000);
}

#include <Arduino.h>
#include <Wire.h>

#include "max6675.h"

const int thermoDO = 4;
const int thermoCS = 5;
const int thermoCLK = 6;

// How long we wait before reading the sensors after each loop
const int READ_INTERVAL = 1;  // Seconds

unsigned int counter = 0;

MAX6675 thermocouple(thermoCLK, thermoCS, thermoDO);

void setup() {
    Serial.begin(9600);

    Serial.println("MAX6675 test");

    delay(500);
}

void loop() {
    float temp = thermocouple.readCelsius();

    Serial.print(counter);
    Serial.print(",");
    Serial.print(temp);
    Serial.println();

    counter++;
    delay(READ_INTERVAL * 1000);
}

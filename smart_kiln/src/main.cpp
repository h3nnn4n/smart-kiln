#include <Arduino.h>
#include <Wire.h>

#include "max6675.h"

int thermoDO = 4;
int thermoCS = 5;
int thermoCLK = 6;

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
    delay(1000);
}

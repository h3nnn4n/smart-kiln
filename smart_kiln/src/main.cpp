#include <Arduino.h>
#include <Wire.h>

void setup() {
	Serial.begin(115200);
	delay(1000);

	pinMode(13, OUTPUT);
}

void loop() {
	Serial.println("Hello world");

	digitalWrite(13, HIGH);
	delay(1000);
	digitalWrite(13, LOW);
	delay(1000);
}

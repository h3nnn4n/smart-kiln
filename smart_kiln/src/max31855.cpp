/*******************************************************************************
 * MAX31855 Library
 * Version: 1.10
 * Date: 24-07-2012
 * Company: Rocket Scream Electronics
 * Website: www.rocketscream.com
 *
 * This is a MAX31855 library for Arduino. Please check our wiki
 * (www.rocketscream.com/wiki) for more information on using this piece of
 * library.
 *
 * This library is licensed under Creative Commons Attribution-ShareAlike 3.0
 * Unported License.
 *
 * Revision  Description
 * ========  ===========
 * 1.10			Added negative temperature support for both junction &
 *thermocouple. 1.00      Initial public release.
 *
 *******************************************************************************/
#include "max31855.h"

MAX31855::MAX31855(unsigned char SCK, unsigned char CS, unsigned char SO) {
    so = SO;
    cs = CS;
    sck = SCK;

    // MAX31855 data output pin
    pinMode(so, INPUT);
    // MAX31855 chip select input pin
    pinMode(cs, OUTPUT);
    // MAX31855 clock input pin
    pinMode(sck, OUTPUT);

    // Default output pins state
    digitalWrite(cs, HIGH);
    digitalWrite(sck, LOW);
}

/*******************************************************************************
 * Name: readThermocouple
 * Description: Read the thermocouple temperature either in Degree Celsius or
 *							 Fahrenheit. Internally,
 *the conversion takes place in the background within 100 ms. Values are updated
 *only when the CS line is high.
 *
 * Argument  	Description
 * =========  	===========
 * 1. unit   	Unit of temperature required: CELSIUS or FAHRENHEIT
 *
 * Return			Description
 * =========		===========
 *	temperature	Temperature of the thermocouple either in Degree Celsius
 *or Fahrenheit. If fault is detected, FAULT_OPEN, FAULT_SHORT_GND or
 *							FAULT_SHORT_VCC will be
 *returned. These fault values are outside of the temperature range the MAX31855
 *is capable of.
 *******************************************************************************/
double MAX31855::readThermocouple(unit_t unit) {
    unsigned long data;
    unsigned long v;
    double temperature;

    // Initialize temperature
    temperature = 0;
    v = 0;

    // Shift in 32-bit of data from MAX31855
    data = readData();

    // If fault is detected
    if (data & 0x00010000) {
	// Check for fault type (3 LSB)
	switch (data & 0x00000007) {
	    // Open circuit
	    case 0x01:
		return FAULT_OPEN;

	    // Thermocouple short to GND
	    case 0x02:
		return FAULT_SHORT_GND;

	    // Thermocouple short to VCC
	    case 0x04:
		return FAULT_SHORT_VCC;
	}

	return FAULT_OPEN;
    }

    // Retrieve thermocouple temperature data and strip redundant data
    data = data >> 18;
    // Serial.println(data, BIN);
    //  Bit-14 is the sign
    v = (data & 0x00001FFF);
    // Serial.println(data, BIN);
    // Serial.println(v * 0.25);

    // Check for negative temperature
    if (data & 0x00002000) {
	// 2's complement operation
	// Invert
	data = ~data;
	// Ensure operation involves lower 13-bit only
	v = data & 0x00001FFF;
	// Add 1 to obtain the positive number
	v += 1;
	// Make temperature negative
	v *= -1;
    }

    // Convert to Degree Celsius
    temperature = v * 0.25;

    // If temperature unit in Fahrenheit is desired
    if (unit == FAHRENHEIT) {
	// Convert Degree Celsius to Fahrenheit
	temperature = (temperature * 9.0 / 5.0) + 32;
    }

    return temperature;
}

/*******************************************************************************
 * Name: readJunction
 * Description: Read the thermocouple temperature either in Degree Celsius or
 *							 Fahrenheit. Internally,
 *the conversion takes place in the background within 100 ms. Values are updated
 *only when the CS line is high.
 *
 * Argument  	Description
 * =========  	===========
 * 1. unit   	Unit of temperature required: CELSIUS or FAHRENHEIT
 *
 * Return			Description
 * =========		===========
 *	temperature	Temperature of the cold junction either in Degree
 *Celsius or Fahrenheit.
 *
 *******************************************************************************/
double MAX31855::readJunction(unit_t unit) {
    double temperature;
    unsigned long data;

    // Shift in 32-bit of data from MAX31855
    data = readData();

    // Strip fault data bits & reserved bit
    data = data >> 4;
    // Bit-12 is the sign
    temperature = (data & 0x000007FF);

    // Check for negative temperature
    if (data & 0x00000800) {
	// 2's complement operation
	// Invert
	data = ~data;
	// Ensure operation involves lower 11-bit only
	temperature = data & 0x000007FF;
	// Add 1 to obtain the positive number
	temperature += 1;
	// Make temperature negative
	temperature *= -1;
    }

    // Convert to Degree Celsius
    temperature *= 0.0625;

    // If temperature unit in Fahrenheit is desired
    if (unit == FAHRENHEIT) {
	// Convert Degree Celsius to Fahrenheit
	temperature = (temperature * 9.0 / 5.0) + 32;
    }

    // Return the temperature
    return (temperature);
}

/*******************************************************************************
 * Name: readData
 * Description: Shift in 32-bit of data from MAX31855 chip. Minimum clock pulse
 *							 width is 100 ns. No
 *delay is required in this case.
 *
 * Argument  	Description
 * =========  	===========
 * 1. NIL
 *
 * Return			Description
 * =========		===========
 *	data				32-bit of data acquired from the
 *MAX31855 chip.
 *
 *******************************************************************************/
unsigned long MAX31855::readData() {
    int bitCount;
    unsigned long data;
    unsigned long v;
    int bit_bang_delay = 100;

    // Clear data
    //while (true) {
	data = 0;

	// Select the MAX31855 chip
	digitalWrite(cs, LOW);
	delayMicroseconds(bit_bang_delay);

	// Serial.println();
	// Serial.println();

	// Shift in 32-bit of data
	for (bitCount = 31; bitCount >= 0; bitCount--) {
	    // Serial.print("bit: ");
	    // Serial.print(bitCount);
	    // if (bitCount < 10)
	    // Serial.print(" ");

	    digitalWrite(sck, HIGH);
	    // delayMicroseconds(bit_bang_delay / 3);
	    delayMicroseconds(bit_bang_delay);

	    // If data bit is high
	    if (digitalRead(so)) {
		// Need to type cast data type to unsigned long, else compiler
		// will truncate to 16-bit
		data |= ((unsigned long)1 << bitCount);
	    }

	    // Serial.print("   ");
	    // Serial.print(data, BIN);
	    // Serial.println();

	    digitalWrite(sck, LOW);
	    delayMicroseconds(bit_bang_delay);
	}

	// Deselect MAX31855 chip
	digitalWrite(cs, HIGH);
	delayMicroseconds(bit_bang_delay);

	return data;
}

double MAX31855::readCelsius() {
    double value = readThermocouple(CELSIUS);
    return value;
}

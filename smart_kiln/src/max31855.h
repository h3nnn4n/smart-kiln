#ifndef	MAX31855_H
#define MAX31855_H

#include "Arduino.h"

#define	FAULT_OPEN		10000
#define	FAULT_SHORT_GND	10001
#define	FAULT_SHORT_VCC	10002

enum	unit_t
{
	CELSIUS,
	FAHRENHEIT
};

class	MAX31855
{
	public:
		MAX31855(unsigned char SO, unsigned	char CS, unsigned char SCK);

		double	readThermocouple(unit_t	unit);
		double	readJunction(unit_t	unit);
		unsigned long readData();

	private:
		unsigned char so;
		unsigned char cs;
		unsigned char sck;


};
#endif


/* I'm using function() {
 * ...
 * }
 * format instead of
 * function()
 * {
 * ...
 * }
 *
 * format. I know it's "wrong." I do not care.
 */

#include "A4988.h"
#include "MultiDriver.h"
#include "SyncDriver.h"
#include "Servo.h"

// Stepper properties
#define STEPS 200
#define MS 16

// Servo 
#define SERVO 6

// Stepper pins
#define X0_STEP 13
#define X0_DIR 12
#define X1_STEP 11
#define X1_DIR 10
#define Y_STEP 9
#define Y_DIR 8
#define EN 7

// Limit switch pins
#define LIMITS 2 // Must be pin 1 or 2 (interrupt pins)
#define LIMIT_X0 3
#define LIMIT_X1 4
#define LIMIT_Y 5

// Voltage sense port
#define LOGIC_V A0

// Constants for each axis
#define X 0
#define Y 1

#define UP 1
#define DOWN 0

#define SQUARES 8
#define CRUISE_RPM 40
#define X_OFFSET 10 * MS
#define Y_OFFSET 12 * MS

// For debugging/utility
#define LED_ON digitalWrite(LED_BUILTIN, HIGH)
#define LED_OFF digitalWrite(LED_BUILTIN, LOW)

// Servo
Servo servo;

// Steppers
A4988 x0(STEPS, X0_DIR, X0_STEP, EN);
A4988 x1(STEPS, X1_DIR, X1_STEP, EN);
A4988 y(STEPS, Y_DIR, Y_STEP, EN);

SyncDriver x(x0, x1);

// Stepper positions
volatile long xPos;
long xMax;

volatile long yPos;
long yMax;

// Coordinate system
// Sizes
int halfSqr;

// Position
unsigned short xHalfSqr;
unsigned short yHalfSqr;

// Interrupt
volatile bool limit;

void setup() {
	// Start the serial
	Serial.begin(115200);
	Serial.setTimeout(1);
	pinMode(LED_BUILTIN, OUTPUT);
	pinMode(LOGIC_V, INPUT);

	pinMode(LIMITS, INPUT);
	pinMode(LIMIT_X0, INPUT);
	pinMode(LIMIT_X1, INPUT);
	pinMode(LIMIT_Y, INPUT);

    servo.attach(SERVO);

	x0.setEnableActiveState(LOW);
	x1.setEnableActiveState(LOW);
	y.setEnableActiveState(LOW);

	x0.begin(60, MS);
	x1.begin(60, MS);
	y.begin(60, MS);

	disable();

	xPos = 0;
	yPos = 0;

	LED_OFF;
	delay(1000); // Wait a little bit so everything is powered

    // Wait until logic voltage reaches/exceeds 4V
	while (analogRead(LOGIC_V) < 768) { 
		delay(25);
	}

	// Enable all
	enable();
	delay(10);

	LED_ON;

	// Run the calibration sequence
	calibrate();
    setRPM(CRUISE_RPM);

    xMax -= (xMax % (SQUARES * 2)); // Evenly divide into half squares
    yMax -= (yMax % (SQUARES * 2));

    halfSqr = xMax / (SQUARES * 2);
    if (xMax > yMax) {
        halfSqr = yMax / (SQUARES * 2);
    }

    xHalfSqr = yHalfSqr = 0;

    // Attach the interrupt after calibration (now the switches should never be pressed)
    limit = false;
    attachInterrupt(digitalPinToInterrupt(LIMITS), stop, RISING);
}

void loop() {
    if (limit) {
        delay(100);
        enable();
        delay(100);

        moveHome();
    }

    while (!Serial.available()) {}
    String ser = Serial.readStringUntil('\n');

    ser.replace(" ", "");

    int sqr1 = ser.substring(0, ser.indexOf(',')).toInt();
    int sqr2 = ser.substring(ser.indexOf(',')).toInt();

    moveToCenter(sqr1, sqr2);

}

/// Calibrates the board
void calibrate() {
	Serial.println("CALIBRATION");
	Serial.println("HOMING TO ORIGIN");

	/*
	 * Distance traveled is given by delta_x = r * theta
	 * -- r is the radius of the pulley (8mm)
	 * -- theta is the angular displacement (2pi for one rotation)
	 *
	 * Therefore the board (30cm x 30cm) can be traversed by 0.3 / 0.016*pi rotations (~6 full rotations)
	 *
	 * There are 2 axes to move and the whole calibration should take less than 30s so...
	 *
	 * 12 rpm is fast enough if there were only one axis, but we'll do 24 for both (but a little slower bc reasons)
	 */
	setRPM(18.0);
	//setRPM(12); // Arbitrary

	// Begin moving an arbitrary number of steps
	long steps = (long)1000 * STEPS * MS;
	x.startMove(-steps, -steps);
	y.startMove(-steps);

	// Controls while loops
	boolean x0Can, x1Can, yCan;
	x0Can = x1Can = yCan = true;

	LED_ON;

	// Wait until all steppers have stopped moving
	while (x0Can || x1Can || yCan) {
        if ((digitalRead(LIMIT_X0) == HIGH) && x0Can) {
            x0.stop();
            x0Can = false;
        }
        if ((digitalRead(LIMIT_X1) == HIGH) && x1Can) {
            x1.stop();
            x1Can = false;
        }
        if ((digitalRead(LIMIT_Y) == HIGH) && yCan) {
            y.stop();
            yCan = false;
        }

	    if (x0Can || x1Can) {
	    	x.nextAction();
	    }

	    if (yCan) {
	    	y.nextAction();
	    }
	}

    moveX(X_OFFSET);
    moveY(Y_OFFSET);
    xPos = yPos = 0;

	LED_OFF;

	delay(500);

	Serial.println("HOMING TO MAXIMA");

	// Begin moving an arbitrary number of steps
	x.startMove(steps, steps);
	y.startMove(steps);

	x0Can = x1Can = yCan = true;

	LED_ON;

    long stepsLeft[] = {0, 0};

	// Wait until all steppers have stopped moving
	while (x0Can || x1Can || yCan) {
	    if (((digitalRead(LIMIT_X0) == HIGH) || (digitalRead(LIMIT_X1)) == HIGH) && x0Can) {
            stepsLeft[X] = x0.stop();
            x1.stop();
            x0Can = false;
            x1Can = false;
        }
        if ((digitalRead(LIMIT_Y) == HIGH) && yCan) {
            stepsLeft[Y] = y.stop();
            yCan = false;

        }

	    if (x0Can || x1Can) {
	    	x.nextAction();
	    }

	    if (yCan) {
	    	y.nextAction();
	    }
	}

    moveX(-X_OFFSET);
    moveY(-Y_OFFSET);
    xPos = xMax = steps - stepsLeft[X] - X_OFFSET;
    yPos = yMax = steps - stepsLeft[Y] - Y_OFFSET;

	Serial.print("CALIBRATION DONE\t");
	Serial.println("xMax: " + String(xMax) + " yMax: " + String(yMax));

	LED_OFF;

	Serial.println("MOVING HOME");
    setRPM(CRUISE_RPM);
	moveHome(); // Return to origin

	disable();
}

void pickupPiece() {
    servo.write(0);
    delay(100);
}

void dropPiece() {
    servo.write(90);
    delay(100);
}

/// Zero indexed direct movement
void moveToCenter(unsigned short xSqr, unsigned short ySqr) {
    // Half square position
    unsigned short realX = xSqr * 2 + 1;
    unsigned short realY = ySqr * 2 + 1;

    /* The slope of the movement
     * NOTE: dy/dx = (dy/dt) / (dx/dt) -> (dy/dx) * (dx/dt) = dy/dt or (m * xRPM = yRPM)
     */
    int m = (realY - yHalfSqr) / (realX - xHalfSqr);

    x0.setRPM(CRUISE_RPM);
    x1.setRPM(CRUISE_RPM);
    y.setRPM(CRUISE_RPM * m);

    long xSteps = realX * halfSqr - xPos;
    long ySteps = realY * halfSqr - yPos;

    moveXY(xSteps, ySteps);

    xHalfSqr = (xSqr + 1) * 2;
    yHalfSqr = (ySqr + 1) * 2;

    delay(50);

    setRPM(CRUISE_RPM);
}

void dragPiece(unsigned short xSqr, unsigned short ySqr) {
    unsigned short realX = xSqr * 2 + 1;
    unsigned short realY = ySqr * 2 + 1;

    int m = yHalfSqr / xHalfSqr;

    x0.setRPM(CRUISE_RPM);
    x1.setRPM(CRUISE_RPM);
    y.setRPM(CRUISE_RPM * m);

    moveXY(-halfSqr, -halfSqr);

    xHalfSqr += halfSqr;
    yHalfSqr += halfSqr;

    setRPM(CRUISE_RPM);

    int xSteps = (realX - 1) * halfSqr - xHalfSqr;
    int ySteps = (realY - 1) * halfSqr - yHalfSqr;

    delay(100);
    moveX(xSteps);
    delay(500);
    moveY(ySteps);
    delay(500);

    x0.setRPM(CRUISE_RPM);
    x1.setRPM(CRUISE_RPM);
    y.setRPM(CRUISE_RPM * m);

    moveXY(halfSqr, halfSqr);

    xHalfSqr = realX;
    yHalfSqr = realY;

    setRPM(CRUISE_RPM);
}

/// Move the two x-axis steppers in sync
void moveX(long steps) {
	LED_ON;

	xPos += steps;

    x.startMove(steps, steps);

	unsigned timeLeft = 1;
	while (timeLeft > 0) {
		timeLeft = x.nextAction();
	}
	LED_OFF;
}

/// Move the y-axis stepper
void moveY(long steps) {
	LED_ON;

	yPos += steps;

    y.startMove(steps);

	unsigned timeLeft = 1;
	while (timeLeft > 0) {
		timeLeft = y.nextAction();
	}
	LED_OFF;
}

void moveXY(long xSteps, long ySteps) {
    LED_ON;

    xPos += xSteps;
	yPos += ySteps;

    x.startMove(xSteps, xSteps);
    y.startMove(ySteps);

    unsigned timeLeft[] = {1, 1};
    while ((timeLeft[X] != 0) || (timeLeft[Y] != 0)) {
        timeLeft[X] = x.nextAction();
        timeLeft[Y] = y.nextAction();
    }
    LED_OFF;
}

/// Move to (0, 0)
void moveHome() {
	LED_ON;
	x.startMove(-xPos, -xPos);
	y.startMove(-yPos);

	xPos = yPos = xHalfSqr = yHalfSqr = 0;

	unsigned timeLeft[] = {1, 1};

	while (timeLeft[X] > 0 || timeLeft[Y] > 0) {
		timeLeft[X] = x.nextAction();
		timeLeft[Y] = y.nextAction();
	}
	LED_OFF;
}

/**
 * @brief Sets the RPM of every stepper.
 *
 * @param rpm 1-200 is usually safe
 */
void setRPM(float rpm) {
	x0.setRPM(rpm);
	x1.setRPM(rpm);
	y.setRPM(rpm);
}

void enable() {
	x0.enable();
	x1.enable();
	y.enable();
}

void disable() {
	x0.disable();
	x1.disable();
	y.disable();
}

/// Interrupt method that stops the steppers and saves steps remaining.
void stop() {
	LED_ON;
    limit = true;
    delayMicroseconds(10);
    LED_OFF;

	// Something has gone very wrong :(
	x0.stop();
	x1.stop();
	y.stop();
	disable();

	LED_ON;
}

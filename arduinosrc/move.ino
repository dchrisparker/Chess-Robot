// Wire Master Writer
// by Nicholas Zambetti <http://www.zambetti.com>

// Demonstrates use of the Wire library
// Writes data to an I2C/TWI slave device
// Refer to the "Wire Slave Receiver" example for use with this

// Created 29 March 2006

// This example code is in the public domain.


#include <Wire.h>

void setup()
{
  Serial.begin(9600);
  Wire.begin(8); // join i2c bus (address optional for master)
  Wire.onReceive(DataReceive);
  Wire.onRequest(DataRequest);
}

String str;
String strSend = "hello";

void loop()
{
  while (Serial.available() > 0) {
    strSend = Serial.readString();
  }

  delay(500);
}


void DataReceive(int numBytes)
{
  while(Wire.available()) 
  { 
    str = Wire.readString();
  }
  Serial.print(str);
}

void DataRequest()
{
  Wire.write("Hello");
}

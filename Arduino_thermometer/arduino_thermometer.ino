#include <DHT.h>

#define DHTPIN 2      // pin pt data
#define DHTTYPE DHT11 // tipul de dht

DHT dht(DHTPIN, DHTTYPE);

int pinA = 13;
int pinB = 12;
int pinC = 11;
int pinD = 10;
int pinE = 9;
int pinF = 8;
int pinG = 7;
int D1 = 5;
int D2 = 6;
int i = 0;
int k = 0;
int j = 0;
int Arduino_Pins[7] = {pinA, pinB, pinC, pinD, pinE, pinF, pinG};
int Segment_Pins[10][7] = {
  {1, 1, 1, 1, 1, 1, 0}, // 0
  {0, 1, 1, 0, 0, 0, 0}, // 1
  {1, 1, 0, 1, 1, 0, 1}, // 2
  {1, 1, 1, 1, 0, 0, 1}, // 3
  {0, 1, 1, 0, 0, 1, 1}, // 4
  {1, 0, 1, 1, 0, 1, 1}, // 5
  {1, 0, 1, 1, 1, 1, 1}, // 6
  {1, 1, 1, 0, 0, 0, 0}, // 7
  {1, 1, 1, 1, 1, 1, 1}, // 8
  {1, 1, 1, 1, 0, 1, 1}  // 9
};

void setup() {
  pinMode(pinA, OUTPUT);
  pinMode(pinB, OUTPUT);
  pinMode(pinC, OUTPUT);
  pinMode(pinD, OUTPUT);
  pinMode(pinE, OUTPUT);
  pinMode(pinF, OUTPUT);
  pinMode(pinG, OUTPUT);
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);

  dht.begin(); // initializere dht
}

void loop() {
  float temperature = dht.readTemperature(); // citire temperatura

  if (isnan(temperature)) {
    temperature = 0;
  }

  // cifra zecilor si cifra unitatilor pentru temperatura
  int tens = (int)temperature / 10;
  int ones = (int)temperature % 10;

  // afisaj temperatura
  for (int n = 0; n < 500; n++) {
    // afisaj
    for (j = 0; j < 7; j++) {
      digitalWrite(Arduino_Pins[j], Segment_Pins[tens][j]);
    }
    digitalWrite(D1, 1);
    digitalWrite(D2, 0);
    delay(1);

    // afisaj
    for (j = 0; j < 7; j++) {
      digitalWrite(Arduino_Pins[j], Segment_Pins[ones][j]);
    }
    digitalWrite(D1, 0);
    digitalWrite(D2, 1);
    delay(1);
  }
}

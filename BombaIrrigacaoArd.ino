#include <Arduino.h>

const int PINO_SENSOR = A0;
const int PINO_RELE   = 7;

const int VALOR_SECO  = 1023;
const int VALOR_UMIDO = 0;

void setup() {
  Serial.begin(9600);
  pinMode(PINO_SENSOR, INPUT);
  pinMode(PINO_RELE, OUTPUT);
  digitalWrite(PINO_RELE, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char caractereRecebido = Serial.read();
    if (caractereRecebido == 'L') {
      digitalWrite(PINO_RELE, HIGH);
    } 
    else if (caractereRecebido == 'D') {
      digitalWrite(PINO_RELE, LOW);
    }
  }

  int leituraBruta = analogRead(PINO_SENSOR);
  int porcentagemUmidade = map(leituraBruta, VALOR_SECO, VALOR_UMIDO, 0, 100);
  porcentagemUmidade = constrain(porcentagemUmidade, 0, 100);

  bool bombaAtiva = digitalRead(PINO_RELE);

  Serial.print("{\"umidade\":");
  Serial.print(porcentagemUmidade);
  Serial.print(",\"bomba\":");
  Serial.print(bombaAtiva ? "true" : "false");
  Serial.print(",\"modo\":\"manual\"}\n");

  delay(500);
}
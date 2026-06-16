#include <Arduino.h>

const int PINO_SENSOR = A0;
const int PINO_RELE   = 7;

// Limites originais do seu sensor
const int VALOR_SECO  = 1023;
const int VALOR_UMIDO = 0;

// Variável que controla se o Arduino toma decisões sozinho
bool modoAutomatico = true; 

void setup() {
  Serial.begin(9600);
  // Define um tempo máximo curto para a leitura da porta serial não travar
  Serial.setTimeout(50); 
  
  pinMode(PINO_SENSOR, INPUT);
  pinMode(PINO_RELE, OUTPUT);
  
  digitalWrite(PINO_RELE, LOW); 
}

void loop() {
  // 1. LER O SENSOR PRIMEIRO (para ter a informação antes de tomar decisões)
  int leituraBruta = analogRead(PINO_SENSOR);
  int porcentagemUmidade = map(leituraBruta, VALOR_SECO, VALOR_UMIDO, 0, 100);
  porcentagemUmidade = constrain(porcentagemUmidade, 0, 100);

  // 2. PROCESSAR COMANDOS DO PYTHON
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    comando.toUpperCase();

    // startsWith() ignora qualquer lixo ou espaço invisível que o Python possa ter enviado
    if (comando.startsWith("A")) {
      modoAutomatico = true;
      // Trava de segurança: Se você voltou pro automático e a terra já passou de 30%, desliga a bomba pra não transbordar
      if (porcentagemUmidade >= 30) {
        digitalWrite(PINO_RELE, LOW);
      }
    } 
    else if (comando.startsWith("M")) {
      modoAutomatico = false;
    }
    else if (comando.startsWith("L")) {
      modoAutomatico = false;
      digitalWrite(PINO_RELE, HIGH); 
    } 
    else if (comando.startsWith("D")) {
      modoAutomatico = false;
      digitalWrite(PINO_RELE, LOW);  
    }
  }

  // 3. AUTOMAÇÃO LÓGICA (Só roda se estiver no modo AUTO)
  if (modoAutomatico) {
    if (porcentagemUmidade < 30) {
      digitalWrite(PINO_RELE, HIGH); 
    } 
    else if (porcentagemUmidade > 50) {
      digitalWrite(PINO_RELE, LOW);
    }
  }

  // 4. VERIFICA O STATUS REAL DO PINO
  bool bombaAtiva = (digitalRead(PINO_RELE) == HIGH);

  // 5. ENVIA O JSON PARA O PYTHON
  Serial.print("{\"umidade\":");
  Serial.print(porcentagemUmidade);
  Serial.print(",\"bomba\":");
  Serial.print(bombaAtiva ? "true" : "false");
  Serial.print(",\"modo\":\"");
  Serial.print(modoAutomatico ? "auto" : "manual");
  Serial.print("\"}\n");

  delay(500);
}
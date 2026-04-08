/*
  estacao.ino — Estação Meteorológica IoT
  ----------------------------------------
  Módulo 5 | Engenharia de Computação | Inteli

  Lê temperatura e umidade do DHT11 (pino 2) e pressão do BMP180 (I2C)
  e envia um objeto JSON via Serial a cada 5 segundos.

  Formato de saída:
    {"temperatura":25.3,"umidade":62.1,"pressao":1013.5}

  Conexões sugeridas:
    DHT11 VCC  → 5V
    DHT11 GND  → GND
    DHT11 DATA → Pino 2 (+ resistor pull-up 10kΩ para 5V)

  Bibliotecas necessárias (instalar via Library Manager):
    - DHT sensor library (Adafruit)
    - Adafruit BMP085 Unified (para BMP180)
    - Adafruit Unified Sensor

  MODO SIMULAÇÃO: se SIMULAR = true, gera valores aleatórios sem sensores físicos.
*/

#include "DHT.h"

#define DHTPIN    2
#define DHTTYPE   DHT11

// ── Altere para false se tiver os sensores físicos conectados ──
#define SIMULAR true

DHT dht(DHTPIN, DHTTYPE);

// Semente para pseudo-aleatoriedade no modo simulação
float temp_sim  = 24.0;
float umid_sim  = 65.0;
float pres_sim  = 1013.0;

void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(0));

#if !SIMULAR
  dht.begin();
  Serial.println("{\"status\":\"sensor_real\"}");
#else
  Serial.println("{\"status\":\"simulacao\"}");
#endif
}

void loop() {
  float temperatura, umidade, pressao;

#if SIMULAR
  // Deriva suave para simular variação natural
  temp_sim += ((float)random(-10, 11)) / 10.0;
  temp_sim  = constrain(temp_sim, 18.0, 35.0);

  umid_sim += ((float)random(-15, 16)) / 10.0;
  umid_sim  = constrain(umid_sim, 30.0, 95.0);

  pres_sim += ((float)random(-5, 6)) / 10.0;
  pres_sim  = constrain(pres_sim, 1005.0, 1025.0);

  temperatura = temp_sim;
  umidade     = umid_sim;
  pressao     = pres_sim;
#else
  temperatura = dht.readTemperature();
  umidade     = dht.readHumidity();
  pressao     = 0;  // Substitua pela leitura do BMP180 se disponível

  if (isnan(temperatura) || isnan(umidade)) {
    Serial.println("{\"erro\":\"falha_sensor\"}");
    delay(5000);
    return;
  }
#endif

  // Monta e envia o JSON
  Serial.print("{");
  Serial.print("\"temperatura\":"); Serial.print(temperatura, 1);
  Serial.print(",\"umidade\":");    Serial.print(umidade, 1);
  Serial.print(",\"pressao\":");    Serial.print(pressao, 1);
  Serial.println("}");

  delay(5000);
}

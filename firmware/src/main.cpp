#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <DHT.h>

// Definicoes do DHT22
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// Objeto e controle de estado do BMP280
Adafruit_BMP280 bmp;
bool bmpAtivo = false;

// Funcao que tenta iniciar e configurar o BMP280
bool inicializarBMP280() {
  if (bmp.begin(0x76) || bmp.begin(0x77)) {
    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                    Adafruit_BMP280::SAMPLING_X2,
                    Adafruit_BMP280::SAMPLING_X16,
                    Adafruit_BMP280::FILTER_X16,
                    Adafruit_BMP280::STANDBY_MS_500);
    return true;
  }
  return false;
}

// Diagnostico rapido caso o barramento I2C nao encontre o BMP280
void diagnosticarBarramentoI2C() {
  Serial.print("   -> [Diagnostico I2C] Varrendo pinos D21/D22... ");
  byte encontrados = 0;
  for (byte endereco = 1; endereco < 127; endereco++) {
    Wire.beginTransmission(endereco);
    if (Wire.endTransmission() == 0) {
      Serial.print("Dispositivo achado em 0x");
      if (endereco < 16) Serial.print("0");
      Serial.print(endereco, HEX);
      Serial.print(" (Chip ID: 0x");
      Serial.print(bmp.sensorID(), HEX);
      Serial.print(") ");
      encontrados++;
    }
  }
  if (encontrados == 0) {
    Serial.println("NENHUM sinal! Verifique VCC, GND comum, SDA (D21) e SCL (D22).");
  } else {
    Serial.println();
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n--- Iniciando Estacao Meteorologica: DHT22 + BMP280 ---");

  // Inicia o barramento I2C (SDA = GPIO 21, SCL = GPIO 22) em 100kHz estavel
  Wire.begin(21, 22);
  Wire.setClock(100000);

  // Inicializa o DHT22
  dht.begin();
  Serial.println("[OK] DHT22 configurado no GPIO 4.");

  // Tenta inicializar o BMP280
  bmpAtivo = inicializarBMP280();
  if (bmpAtivo) {
    Serial.println("[OK] BMP280 detectado e configurado com sucesso!");
  } else {
    Serial.println("[ALERTA] BMP280 nao respondeu no boot. Tentando reconectar no loop...");
    diagnosticarBarramentoI2C();
  }

  Serial.println("Setup finalizado. Lendo dados...\n");
}

void loop() {
  delay(2000); // Intervalo minimo exigido pelo DHT22

  Serial.println("==================================================");

  // 1. Leitura do DHT22
  float dht_umidade = dht.readHumidity();
  float dht_temp = dht.readTemperature();

  if (isnan(dht_umidade) || isnan(dht_temp)) {
    Serial.println("[DHT22]  ERRO: Falha na leitura! Verifique o pino D4 e alimentacao.");
  } else {
    Serial.print("[DHT22]  Temp: ");
    Serial.print(dht_temp);
    Serial.print(" °C | Umidade: ");
    Serial.print(dht_umidade);
    Serial.println(" %");
  }

  // 2. Reconexao automatica do BMP280 se estiver inativo
  if (!bmpAtivo) {
    bmpAtivo = inicializarBMP280();
    if (bmpAtivo) {
      Serial.println("[BMP280] Reconectado automaticamente!");
    }
  }

  // 3. Leitura do BMP280
  if (bmpAtivo) {
    float bmp_temp = bmp.readTemperature();
    float bmp_pressao = bmp.readPressure() / 100.0F;
    float bmp_altitude = bmp.readAltitude(1013.25);

    // Se a leitura vier corrompida (fio soltou no meio), forca nova inicializacao
    if (isnan(bmp_temp) || isnan(bmp_pressao) || bmp_pressao == 0) {
      Serial.println("[BMP280] ERRO: Leitura corrompida (NaN). Reiniciando sensor...");
      bmpAtivo = false;
      diagnosticarBarramentoI2C();
    } else {
      Serial.print("[BMP280] Temp: ");
      Serial.print(bmp_temp);
      Serial.print(" °C | Pressao: ");
      Serial.print(bmp_pressao);
      Serial.print(" hPa | Alt. Aprox: ");
      Serial.print(bmp_altitude);
      Serial.println(" m");
    }
  } else {
    Serial.println("[BMP280] Desconectado / Sem resposta I2C.");
    diagnosticarBarramentoI2C();
  }
}
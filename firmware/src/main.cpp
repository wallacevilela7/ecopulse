#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <DHT.h>
#include <math.h>

// ================= CONFIGURACAO DE CREDENCIAIS =================
// As credenciais sao lidas de config.h (ignorado pelo .gitignore)
#if __has_include("config.h")
  #include "config.h"
#elif __has_include("../include/config.h")
  #include "../include/config.h"
#endif

#ifndef WIFI_SSID
  #define WIFI_SSID     "SEU_SSID_AQUI"
  #define WIFI_PASSWORD "SUA_SENHA_AQUI"
#endif

const char* ssid     = WIFI_SSID;
const char* password = WIFI_PASSWORD;

// Servidor Web (Porta 80) e Servidor de Stream Serial/Telnet (Porta 23)
WebServer server(80);
WiFiServer telnetServer(23);
WiFiClient telnetClient;

// ================= SENSORES =================

// 1. Sensor Digital de Temperatura e Umidade (DHT22)
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// 2. Sensor Barometrico de Pressao e Altitude (BMP280 - I2C)
Adafruit_BMP280 bmp;
bool bmpAtivo = false;

// 3. Sensor de Qualidade do Ar e Gases (MQ-135 - ADC1)
#define MQ135_PIN 32               // Pino GPIO 32 (Canal ADC1 - opera simultaneo com Wi-Fi)
const float DIVISOR_R1 = 1000.0f;  // Resistor R1 = 1 kΩ (sinal AO do sensor ao pino)
const float DIVISOR_R2 = 2000.0f;  // Resistor R2 = 2 kΩ (pino ao GND)
// Fator atenuador inverso: V_sensor = V_pino * ((R1 + R2) / R2) = V_pino * 1.5
const float FATOR_DIVISOR_MQ135 = (DIVISOR_R1 + DIVISOR_R2) / DIVISOR_R2;

// Parametros da curva de resposta do MQ-135 (Datasheet: PPM = A * (Rs/R0)^B)
const float MQ135_RL = 10.0f;      // Resistor de carga RL tipico na placa = 10 kΩ
const float MQ135_A  = 116.602f;   // Coeficiente A para CO2 e gases atmosfericos
const float MQ135_B  = -2.769f;    // Coeficiente exponencial B
const float MQ135_R0 = 33.90f;     // R0 calibrado para ar ambiente limpo (~400-420 ppm)

// Tempo de pre-aquecimento recomendado do filamento interno (3 minutos = 180 segundos)
const unsigned long TEMPO_PRE_AQUECIMENTO_MS = 180000;

// Estrutura de dados para o MQ-135
struct MQ135Data {
  int rawAdc;
  float pinVoltageV;
  float sensorVoltageV;
  float estimatedPpm;
  bool isWarmedUp;
  String airQualityClass;
  String status;
};

// 4. Sensor de Luminosidade Ambiente (LDR 5mm - ADC1)
#define LDR_PIN 35                 // Pino GPIO 35 (Canal ADC1 - pino de entrada exclusiva)

// Estrutura de dados para o LDR
struct LDRData {
  int rawAdc;
  float voltageV;
  float luminosityPct;
  String condicao;
  String status;
};

// 5. Sensor de Chuva / Pluviometro (Placa condutiva com modulo LM393 - ADC1)
#define RAIN_PIN 34                // Pino GPIO 34 (Canal ADC1 - pino de entrada exclusiva)
const int CHUVA_LIMIAR_SECO = 3800; // Acima deste valor ADC a placa condutiva esta seca

// Estrutura de dados para o Sensor de Chuva
struct RainData {
  int rawAdc;
  float voltageV;
  float intensityPct;
  bool isRaining;
  String condicao;
  String status;
};

// Controle de tempo (substitui o delay para nao travar o Wi-Fi)
unsigned long ultimaLeitura = 0;
const unsigned long intervaloLeitura = 2000;

// Historico recente para exibir no navegador igual ao Monitor Serial
String historicoLog = "";

// Funcao que envia o texto simultaneamente para o USB, Terminal Wi-Fi e Historico Web
void enviarOutput(String texto) {
  // 1. Envia para a porta USB (se estiver conectada)
  Serial.print(texto);

  // 2. Envia em tempo real para o Terminal via Wi-Fi (Netcat / Telnet)
  if (telnetClient && telnetClient.connected()) {
    telnetClient.print(texto);
  }

  // 3. Salva no buffer da pagina Web (mantem os ultimos ~2500 caracteres)
  historicoLog += texto;
  if (historicoLog.length() > 2500) {
    int corte = historicoLog.indexOf("==================================================", 300);
    if (corte != -1) {
      historicoLog = historicoLog.substring(corte);
    } else {
      historicoLog = historicoLog.substring(historicoLog.length() - 2000);
    }
  }
}

// Funcao com multisampling para filtrar ruidos eletricos de alta frequencia do ADC
int lerAdcMedio(int pino, int amostras = 16) {
  long soma = 0;
  for (int i = 0; i < amostras; i++) {
    soma += analogRead(pino);
    delayMicroseconds(50);
  }
  return (int)(soma / amostras);
}

// Obtem a tensao real medida no pino com base na calibracao do chip ESP32
float lerTensaoPino(int pino, int rawAdc) {
  #if defined(ESP32)
    long somaMv = 0;
    for (int i = 0; i < 8; i++) {
      somaMv += analogReadMilliVolts(pino);
      delayMicroseconds(50);
    }
    float vPino = (somaMv / 8.0f) / 1000.0f;
    if (vPino > 0.02f) {
      return vPino;
    }
  #endif
  // Fallback linear (resolucao 12 bits, tensao nominal 3.3V)
  return (rawAdc / 4095.0f) * 3.3f;
}

// Executa a aquisicao completa e os calculos de qualidade do ar do MQ-135
MQ135Data lerMQ135() {
  MQ135Data dados;

  // 1. Leitura analógica média com filtro anti-ruído
  dados.rawAdc = lerAdcMedio(MQ135_PIN, 16);

  // 2. Tensão real presente no pino GPIO 32 (após divisor 1k/2k, faixa 0 - 3.3V)
  dados.pinVoltageV = lerTensaoPino(MQ135_PIN, dados.rawAdc);

  // 3. Reconstituição da tensão de saída original gerada pelo sensor (faixa 0 - 5.0V)
  dados.sensorVoltageV = dados.pinVoltageV * FATOR_DIVISOR_MQ135;
  if (dados.sensorVoltageV > 5.0f) {
    dados.sensorVoltageV = 5.0f;
  }

  // 4. Verificação de pré-aquecimento do filamento térmico
  unsigned long tempoAtual = millis();
  dados.isWarmedUp = (tempoAtual >= TEMPO_PRE_AQUECIMENTO_MS);

  // 5. Verificação de conexão física
  if (dados.sensorVoltageV < 0.05f) {
    dados.status = "ERRO: Sensor desconectado ou sem alimentacao no barramento 5V";
    dados.estimatedPpm = 0.0f;
    dados.airQualityClass = "DESCONHECIDO";
    return dados;
  }

  if (dados.sensorVoltageV >= 4.95f) {
    dados.status = "ALERTA: Saturacao maxima do sensor (5.0V)";
    dados.estimatedPpm = 9999.0f;
    dados.airQualityClass = "SATURADO";
    return dados;
  }

  // 6. Cálculo da resistência interna do sensor Rs:
  // V_sensor = Vc * RL / (Rs + RL) => Rs = RL * (Vc - V_sensor) / V_sensor
  float rs = MQ135_RL * ((5.0f - dados.sensorVoltageV) / dados.sensorVoltageV);
  if (rs < 0.01f) rs = 0.01f;

  // 7. Estimativa de concentração de gases em PPM pela curva de lei de potência:
  // PPM = A * (Rs / R0)^B
  float ratio = rs / MQ135_R0;
  dados.estimatedPpm = MQ135_A * pow(ratio, MQ135_B);

  // Limitador de faixa plausível para exibição
  if (dados.estimatedPpm < 10.0f) dados.estimatedPpm = 10.0f;
  if (dados.estimatedPpm > 10000.0f) dados.estimatedPpm = 10000.0f;

  // 8. Classificação categórica da qualidade do ar
  if (dados.estimatedPpm < 600.0f) {
    dados.airQualityClass = "EXCELENTE";
  } else if (dados.estimatedPpm < 1000.0f) {
    dados.airQualityClass = "BOA";
  } else if (dados.estimatedPpm < 1500.0f) {
    dados.airQualityClass = "MODERADA";
  } else if (dados.estimatedPpm < 2000.0f) {
    dados.airQualityClass = "RUIM";
  } else {
    dados.airQualityClass = "CRITICA";
  }

  dados.status = "OK";
  return dados;
}

// Executa a leitura da intensidade de luz ambiente pelo LDR (GPIO 34)
LDRData lerLDR() {
  LDRData dados;
  dados.rawAdc = lerAdcMedio(LDR_PIN, 16);
  dados.voltageV = lerTensaoPino(LDR_PIN, dados.rawAdc);

  // Em modulos LDR comerciais de 4 pinos (LM393):
  // O circuito interno e: VCC (3.3V) -> Resistor 10k -> Pino AO -> LDR -> GND
  // - No escuro: R_ldr e altissima (~100k+) -> AO fica perto de 3.3V (ADC alto ~3800-4095)
  // - Sob luz/flash: R_ldr cai drasticamente (<1k) -> AO cai perto de 0V (ADC baixo ~100-600)
  // Portanto, a luminosidade e INVERSAMENTE proporcional ao ADC do pino AO:
  dados.luminosityPct = (1.0f - (dados.rawAdc / 4095.0f)) * 100.0f;
  if (dados.luminosityPct < 0.0f) dados.luminosityPct = 0.0f;
  if (dados.luminosityPct > 100.0f) dados.luminosityPct = 100.0f;

  // Classificação ambiental da luz calibrada
  if (dados.luminosityPct < 15.0f) {
    dados.condicao = "ESCURO (Noite / Coberto)";
  } else if (dados.luminosityPct < 45.0f) {
    dados.condicao = "LUZ BAIXA (Penumbra)";
  } else if (dados.luminosityPct < 75.0f) {
    dados.condicao = "MODERADA (Ambiente Interno / Nublado)";
  } else {
    dados.condicao = "ALTA (Luz Intensa / Flash / Ensolarado)";
  }

  dados.status = "OK";
  return dados;
}

// Executa a leitura do sensor de chuva / placa pluviometrica (GPIO 35)
RainData lerChuva() {
  RainData dados;
  dados.rawAdc = lerAdcMedio(RAIN_PIN, 16);
  dados.voltageV = lerTensaoPino(RAIN_PIN, dados.rawAdc);

  // Comportamento: Placa seca = ADC alto (~4095). Placa molhada = ADC baixo (~0-1500).
  // Invertemos a relacao para que 0% = seco e 100% = totalmente submerso/encharcado.
  dados.intensityPct = (1.0f - (dados.rawAdc / 4095.0f)) * 100.0f;
  if (dados.intensityPct < 0.0f) dados.intensityPct = 0.0f;
  if (dados.intensityPct > 100.0f) dados.intensityPct = 100.0f;

  // Limiar de deteccao de chuva ativa
  dados.isRaining = (dados.rawAdc < CHUVA_LIMIAR_SECO && dados.intensityPct >= 5.0f);

  if (!dados.isRaining) {
    dados.condicao = "SECO (Sem Chuva)";
  } else if (dados.intensityPct < 25.0f) {
    dados.condicao = "GAROA (Chuva Leve)";
  } else if (dados.intensityPct < 65.0f) {
    dados.condicao = "CHUVA MODERADA";
  } else {
    dados.condicao = "CHUVA FORTE / TORRENCIAL";
  }

  dados.status = "OK";
  return dados;
}

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

String diagnosticarBarramentoI2C() {
  String msg = "   -> [Diagnostico I2C] Varrendo pinos D21/D22... ";
  byte encontrados = 0;
  for (byte endereco = 1; endereco < 127; endereco++) {
    Wire.beginTransmission(endereco);
    if (Wire.endTransmission() == 0) {
      msg += "Dispositivo achado em 0x";
      if (endereco < 16) msg += "0";
      msg += String(endereco, HEX);
      msg += " (Chip ID: 0x" + String(bmp.sensorID(), HEX) + ") ";
      encontrados++;
    }
  }
  if (encontrados == 0) {
    msg += "NENHUM sinal! Verifique VCC, GND comum, SDA (D21) e SCL (D22).\n";
  } else {
    msg += "\n";
  }
  return msg;
}

void configurarRotasWeb() {
  // Rota principal: Tela preta identica ao Monitor Serial no navegador
  server.on("/", []() {
    String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'>";
    html += "<meta http-equiv='refresh' content='2'>";
    html += "<title>EcoPulse - Monitor Serial Wi-Fi (5 Sensores)</title>";
    html += "<style>body{background:#121212;color:#00ff66;font-family:monospace;padding:20px;font-size:15px;}";
    html += "pre{white-space:pre-wrap;word-wrap:break-word;}</style></head><body>";
    html += "<h3>EcoPulse - Monitor Remoto Wi-Fi (5 Sensores) | IP: " + WiFi.localIP().toString() + "</h3><hr>";
    html += "<pre>" + historicoLog + "</pre>";
    html += "<script>window.scrollTo(0,document.body.scrollHeight);</script>";
    html += "</body></html>";
    server.send(200, "text/html", html);
  });

  // Rota de texto puro (para usar com curl no terminal)
  server.on("/raw", []() {
    server.send(200, "text/plain", historicoLog);
  });
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // 1. Inicializacao dos barramentos e sensores digitais
  Wire.begin(21, 22);
  Wire.setClock(100000);
  dht.begin();
  bmpAtivo = inicializarBMP280();

  // 2. Configuracao dos canais analogicos no ADC1 (operam com Wi-Fi ativo)
  pinMode(MQ135_PIN, INPUT);
  pinMode(LDR_PIN, INPUT);
  pinMode(RAIN_PIN, INPUT);
  #if defined(ESP32)
    analogSetPinAttenuation(MQ135_PIN, ADC_11db); // Escala completa de tensao ate ~3.3V
    analogSetPinAttenuation(LDR_PIN, ADC_11db);
    analogSetPinAttenuation(RAIN_PIN, ADC_11db);
  #endif

  // 3. Conexao Wi-Fi
  Serial.println("\nConectando ao Wi-Fi: " + String(ssid));
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 30) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[OK] Wi-Fi Conectado!");
    Serial.print("   -> Endereco IP: ");
    Serial.println(WiFi.localIP());
    if (MDNS.begin("esp32")) {
      Serial.println("   -> Endereco mDNS: http://esp32.local");
    }
    server.begin();
    configurarRotasWeb();
    telnetServer.begin();
    telnetServer.setNoDelay(true);
    Serial.println("   -> Stream de Terminal ativo na porta 23.");
  } else {
    Serial.println("\n[ERRO] Nao foi possivel conectar ao Wi-Fi. Rodando offline.");
  }

  enviarOutput("\n==================================================\n");
  enviarOutput(" Estacao Meteorologica EcoPulse - 5 Sensores Ativos\n");
  enviarOutput("==================================================\n");
  enviarOutput("[OK] DHT22 configurado no GPIO 4 (Digital).\n");
  if (bmpAtivo) {
    enviarOutput("[OK] BMP280 detectado no barramento I2C (SDA: D21 / SCL: D22).\n");
  } else {
    enviarOutput("[ALERTA] BMP280 nao respondeu no boot. Tentando reconectar no loop...\n");
    enviarOutput(diagnosticarBarramentoI2C());
  }
  enviarOutput("[OK] MQ-135 configurado no GPIO 32 (ADC1) com divisor 1k/2k (fator 1.5x).\n");
  enviarOutput("[OK] LDR (Luz) configurado no GPIO " + String(LDR_PIN) + " (ADC1 - 3.3V).\n");
  enviarOutput("[OK] Pluviometro (Chuva) configurado no GPIO " + String(RAIN_PIN) + " (ADC1 - 3.3V).\n");
  enviarOutput("     Tempo de pre-aquecimento MQ-135: 180s (3 minutos).\n");
  enviarOutput("Setup finalizado. Lendo todos os sensores a cada 2s...\n\n");
}

void loop() {
  // Reconecta o Wi-Fi automaticamente se o sinal cair
  if (WiFi.status() == WL_CONNECTED) {
    server.handleClient();

    // Verifica se voce abriu uma conexao de terminal (Netcat/Telnet)
    if (telnetServer.hasClient()) {
      if (!telnetClient || !telnetClient.connected()) {
        if (telnetClient) telnetClient.stop();
        telnetClient = telnetServer.available();
        telnetClient.println("--- Conectado ao Monitor Serial Wi-Fi da ESP32 ---");
      } else {
        telnetServer.available().stop(); // Rejeita conexoes extras
      }
    }
  }

  // Executa a leitura exatamente a cada 2 segundos sem bloquear o processador
  if (millis() - ultimaLeitura >= intervaloLeitura) {
    ultimaLeitura = millis();

    String bloco = "==================================================\n";

    // 1. Leitura do DHT22 (Temperatura e Umidade)
    float dht_umidade = dht.readHumidity();
    float dht_temp = dht.readTemperature();

    if (isnan(dht_umidade) || isnan(dht_temp)) {
      bloco += "[DHT22]   ERRO: Falha na leitura! Verifique o pino D4 e alimentacao.\n";
    } else {
      bloco += "[DHT22]   Temp: " + String(dht_temp, 2) + " °C | Umidade: " + String(dht_umidade, 2) + " %\n";
    }

    // 2. Reconexao automatica do BMP280 se estiver inativo
    if (!bmpAtivo) {
      bmpAtivo = inicializarBMP280();
      if (bmpAtivo) {
        bloco += "[BMP280]  Reconectado automaticamente!\n";
      }
    }

    // Leitura do BMP280 (Pressao, Temperatura e Altitude)
    if (bmpAtivo) {
      float bmp_temp = bmp.readTemperature();
      float bmp_pressao = bmp.readPressure() / 100.0F;
      float bmp_altitude = bmp.readAltitude(1013.25);

      if (isnan(bmp_temp) || isnan(bmp_pressao) || bmp_pressao == 0) {
        bloco += "[BMP280]  ERRO: Leitura corrompida (NaN). Reiniciando sensor...\n";
        bmpAtivo = false;
        bloco += diagnosticarBarramentoI2C();
      } else {
        bloco += "[BMP280]  Temp: " + String(bmp_temp, 2) + " °C | Pressao: " + String(bmp_pressao, 2) + " hPa | Alt. Aprox: " + String(bmp_altitude, 2) + " m\n";
      }
    } else {
      bloco += "[BMP280]  Desconectado / Sem resposta I2C.\n";
      bloco += diagnosticarBarramentoI2C();
    }

    // 3. Leitura do MQ-135 (Qualidade do Ar e Gases)
    MQ135Data mq = lerMQ135();
    if (mq.status != "OK") {
      bloco += "[MQ-135]  " + mq.status + " (ADC: " + String(mq.rawAdc) + ")\n";
    } else {
      bloco += "[MQ-135]  ADC: " + String(mq.rawAdc);
      bloco += " | Pino: " + String(mq.pinVoltageV, 2) + " V";
      bloco += " | Sensor: " + String(mq.sensorVoltageV, 2) + " V";
      bloco += " | PPM: " + String(mq.estimatedPpm, 1);
      bloco += " | Ar: " + mq.airQualityClass;
      if (!mq.isWarmedUp) {
        unsigned long segRestantes = (TEMPO_PRE_AQUECIMENTO_MS - millis()) / 1000;
        bloco += " (Aquecendo: restam " + String(segRestantes) + "s)";
      } else {
        bloco += " [Estabilizado]";
      }
      bloco += "\n";
    }

    // 4. Leitura do LDR (Luminosidade Ambiente)
    LDRData ldr = lerLDR();
    bloco += "[LDR]     ADC: " + String(ldr.rawAdc);
    bloco += " | Pino: " + String(ldr.voltageV, 2) + " V";
    bloco += " | Luz: " + String(ldr.luminosityPct, 1) + " %";
    bloco += " | " + ldr.condicao + "\n";

    // 5. Leitura do Sensor de Chuva / Pluviômetro
    RainData rain = lerChuva();
    bloco += "[CHUVA]   ADC: " + String(rain.rawAdc);
    bloco += " | Pino: " + String(rain.voltageV, 2) + " V";
    bloco += " | Agua: " + String(rain.intensityPct, 1) + " %";
    bloco += " | Chuva: " + String(rain.isRaining ? "SIM" : "NAO");
    bloco += " (" + rain.condicao + ")\n";

    // Dispara o bloco identico para todos os canais (USB, Terminal Wi-Fi e Web)
    enviarOutput(bloco);
  }
}
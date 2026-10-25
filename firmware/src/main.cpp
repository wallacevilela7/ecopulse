#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <DHT.h>

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
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

Adafruit_BMP280 bmp;
bool bmpAtivo = false;

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
    html += "<title>Monitor Serial Wi-Fi - ESP32</title>";
    html += "<style>body{background:#121212;color:#00ff66;font-family:monospace;padding:20px;font-size:15px;}";
    html += "pre{white-space:pre-wrap;word-wrap:break-word;}</style></head><body>";
    html += "<h3>Monitor Serial Remoto (ESP32 Wi-Fi) - IP: " + WiFi.localIP().toString() + "</h3><hr>";
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

  Wire.begin(21, 22);
  Wire.setClock(100000);
  dht.begin();
  bmpAtivo = inicializarBMP280();

  // Conexao Wi-Fi
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

  enviarOutput("\n--- Iniciando Estacao Meteorologica: DHT22 + BMP280 ---\n");
  enviarOutput("[OK] DHT22 configurado no GPIO 4.\n");
  if (bmpAtivo) {
    enviarOutput("[OK] BMP280 detectado e configurado com sucesso!\n");
  } else {
    enviarOutput("[ALERTA] BMP280 nao respondeu no boot. Tentando reconectar no loop...\n");
    enviarOutput(diagnosticarBarramentoI2C());
  }
  enviarOutput("Setup finalizado. Lendo dados...\n\n");
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

    // 1. Leitura do DHT22
    float dht_umidade = dht.readHumidity();
    float dht_temp = dht.readTemperature();

    if (isnan(dht_umidade) || isnan(dht_temp)) {
      bloco += "[DHT22]  ERRO: Falha na leitura! Verifique o pino D4 e alimentacao.\n";
    } else {
      bloco += "[DHT22]  Temp: " + String(dht_temp, 2) + " °C | Umidade: " + String(dht_umidade, 2) + " %\n";
    }

    // 2. Reconexao automatica do BMP280 se estiver inativo
    if (!bmpAtivo) {
      bmpAtivo = inicializarBMP280();
      if (bmpAtivo) {
        bloco += "[BMP280] Reconectado automaticamente!\n";
      }
    }

    // 3. Leitura do BMP280
    if (bmpAtivo) {
      float bmp_temp = bmp.readTemperature();
      float bmp_pressao = bmp.readPressure() / 100.0F;
      float bmp_altitude = bmp.readAltitude(1013.25);

      if (isnan(bmp_temp) || isnan(bmp_pressao) || bmp_pressao == 0) {
        bloco += "[BMP280] ERRO: Leitura corrompida (NaN). Reiniciando sensor...\n";
        bmpAtivo = false;
        bloco += diagnosticarBarramentoI2C();
      } else {
        bloco += "[BMP280] Temp: " + String(bmp_temp, 2) + " °C | Pressao: " + String(bmp_pressao, 2) + " hPa | Alt. Aprox: " + String(bmp_altitude, 2) + " m\n";
      }
    } else {
      bloco += "[BMP280] Desconectado / Sem resposta I2C.\n";
      bloco += diagnosticarBarramentoI2C();
    }

    // Dispara o bloco identico para todos os canais (USB, Terminal Wi-Fi e Web)
    enviarOutput(bloco);
  }
}
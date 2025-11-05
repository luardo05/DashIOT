// --- MQ-2 + ESP32-C3 Super Mini com Conectividade Wi-Fi e MQTT ---

// Bibliotecas para Wi-Fi, MQTT e manipulação de JSON
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// =========== Configurações de Wi-Fi =============
const char* ssid = "SENAC-Mesh";      // << COLOQUE O NOME DA SUA REDE WI-FI AQUI
const char* password = "09080706"; // << COLOQUE A SENHA DA SUA REDE WI-FI AQUI

// =========== Configurações do MQTT =============
const char* mqtt_server = "broker.hivemq.com"; // Broker MQTT público e gratuito
const int mqtt_port = 1883;
// Tópico para onde os dados do sensor de gás serão enviados
const char* mqtt_topic = "br/com/meuprojeto/esp32c3/mq2";
// ID único para seu dispositivo. Mude se tiver mais de um ESP32.
const char* client_id = "esp32-c3-supermini-mq2-sensor";

// =========== Objetos de Rede =============
WiFiClient espClient;
PubSubClient client(espClient);

// =========== Definições dos Pinos do Sensor MQ-2 =============
#define PIN_ANALOGICO 3  // A0 do sensor conectado ao GPIO3
#define PIN_DIGITAL   4  // D0 do sensor conectado ao GPIO4

// =========== Controle de Tempo =============
const unsigned long INTERVALO_ENVIO = 5000; // Intervalo de 5 segundos entre os envios
unsigned long tempoUltimoEnvio = 0;

// Variáveis para armazenar as leituras
int valorAnalogico = 0;
int valorDigital = 0;

// Função para suavizar leitura analógica (do seu código original)
int leituraMediaAnalogica(int pino, int amostras = 10) {
  long soma = 0;
  for (int i = 0; i < amostras; i++) {
    soma += analogRead(pino);
    delay(10);
  }
  return soma / amostras;
}

// --- Funções de Conectividade (Adaptadas do código 2) ---

// Função para conectar ao Wi-Fi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

// Função para reconectar ao Broker MQTT se a conexão cair
void reconnect_mqtt() {
  while (!client.connected()) {
    Serial.print("Tentando conectar ao MQTT Broker...");
    if (client.connect(client_id)) {
      Serial.println("Conectado!");
    } else {
      Serial.print("falhou, rc=");
      Serial.print(client.state());
      Serial.println(" tentando novamente em 5 segundos");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_DIGITAL, INPUT);
  delay(1000);

  Serial.println("\n=== Teste MQ-2 com ESP32-C3 e MQTT ===");

  // Inicia a conexão Wi-Fi
  setup_wifi();

  // Aponta o cliente MQTT para o servidor/broker
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  // Garante que o ESP32 esteja sempre conectado ao Broker MQTT
  if (!client.connected()) {
    reconnect_mqtt();
  }
  // Essencial para manter a conexão MQTT viva e processar mensagens
  client.loop();

  // Lógica para enviar dados apenas no intervalo definido, sem usar delay()
  unsigned long agora = millis();
  if (agora - tempoUltimoEnvio >= INTERVALO_ENVIO) {
    tempoUltimoEnvio = agora; // Atualiza o tempo do último envio

    // --- Leitura do Sensor MQ-2 (Lógica do seu código original) ---
    valorAnalogico = leituraMediaAnalogica(PIN_ANALOGICO);
    valorDigital = digitalRead(PIN_DIGITAL);

    // Exibe os resultados no Serial Monitor local
    Serial.print("Leitura analogica: ");
    Serial.print(valorAnalogico);
    Serial.print(" | Leitura digital: ");
    Serial.println(valorDigital == LOW ? "GÁS DETECTADO" : "Sem gás detectado");

    // --- Envio dos Dados via MQTT ---
    
    // Cria o objeto JSON para enviar os dados
    JsonDocument doc;
    doc["valorAnalogico"] = valorAnalogico;
    // Converte o valor digital (0 ou 1) para uma string mais descritiva
    doc["status"] = (valorDigital == LOW) ? "GAS_DETECTADO" : "NORMAL";

    // Converte o JSON para uma string
    char json_output[128];
    serializeJson(doc, json_output);

    // Publica a string no tópico MQTT
    Serial.print("Publicando no topico ");
    Serial.print(mqtt_topic);
    Serial.print(": ");
    Serial.println(json_output);

    client.publish(mqtt_topic, json_output);
  }
}
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// ===================== WiFi 설정 =====================
const char* WIFI_SSID     = "iPhone";
const char* WIFI_PASSWORD = "123456";


// ===================== MQTT 설정 =====================
const char* MQTT_BROKER_HOST = "k13e103.p.ssafy.io";  // EC2/Mosquitto IP
const int   MQTT_BROKER_PORT = 1883;

const char* MQTT_USERNAME = "admin";
const char* MQTT_PASSWORD = "ssafy";

// 토픽 이름 (필요하면 바꿔도 됨)
const char* TOPIC_CAPTURE = "arduino/camera/trigger"; // Mega → AI
const char* TOPIC_RESULT  = "ai/inductor/result";  // AI → Mega
const char* TOPIC_TH      = "arduino/th/data"; 

WiFiClient espClient;
PubSubClient mqttClient(espClient);

// ======================= Mega와의 UART (Serial2) =======================
// Mega TX1(18) → ESP32 RX2(16)
// Mega RX1(19) → ESP32 TX2(17)
#define MEGA_RX_PIN 16   
#define MEGA_TX_PIN 17 
HardwareSerial MegaSerial(2);  // Serial2 사용

// ===================== DHT 온습도 센서 설정 =====================
#define DHTPIN   28      // ESP32의 GPIO 번호 (원하는 핀으로 변경, 예: 4)
#define DHTTYPE  DHT22  // 센서 타입: DHT11, DHT22 등

DHT dht(DHTPIN, DHTTYPE);

// 1분마다 보내기 위한 타이머
unsigned long lastThSentMs = 0;
const unsigned long TH_SEND_INTERVAL = 60000; // 60초(1분)

// ===================== 함수 선언 =====================
void connectWiFi();
void connectMQTT();
void mqttCallback(char* topic, byte* payload, unsigned int length);
void handleSerialFromMega();
void sendThIfDue();

// ===================== setup =====================
void setup() {
  Serial.begin(115200);          // 디버깅용
  MegaSerial.begin(115200, SERIAL_8N1, MEGA_RX_PIN, MEGA_TX_PIN);

    dht.begin();      // 온습도 센서 초기화

  connectWiFi();

  mqttClient.setServer(MQTT_BROKER_HOST, MQTT_BROKER_PORT);
  mqttClient.setCallback(mqttCallback);

  connectMQTT();

  Serial.println("ESP32 MQTT Bridge Started");
}

// ===================== loop =====================
void loop() {
  if (!mqttClient.connected()) {
    connectMQTT();
  }
  mqttClient.loop();

   // 1분마다 온습도 publish
  sendThIfDue();           

  // Mega에서 오는 CAPTURE 등 처리
  handleSerialFromMega();
}

// ===================== WiFi 연결 =====================
void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("와이파이 연결중.");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// ===================== MQTT 연결 =====================
void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Connecting to MQTT... ");
    String clientId = "ESP32-MEGA-BRIDGE-";
    clientId += String(random(0xFFFF), HEX);

    bool ok;
    if (strlen(MQTT_USERNAME) > 0) {
      ok = mqttClient.connect(clientId.c_str(), MQTT_USERNAME, MQTT_PASSWORD);
    } else {
      ok = mqttClient.connect(clientId.c_str());
    }

    if (ok) {
      Serial.println("connected!");

      // 결과 토픽 구독
      mqttClient.subscribe(TOPIC_RESULT);
      Serial.print("Subscribed: ");
      Serial.println(TOPIC_RESULT);
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" retry in 2 seconds");
      delay(2000);
    }
  }
}

// ===================== MQTT 콜백 =====================
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String t = String(topic);
  String message;

  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.print("[ESP32] MQTT Received [");
  Serial.print(t);
  Serial.print("] ");
  Serial.println(message);

  // AI 서버 → 결과 토픽: "A0" 또는 "B1" 형식이라고 가정
  if (t == String(TOPIC_RESULT)) {
    // Mega로 그대로 전달
    MegaSerial.println(message);
    Serial.print("[ESP32] Forwarded to Mega: ");
    Serial.println(message);
  }
}

// ===================== Mega → ESP32 → MQTT =====================
// MegaSerial에서 한 줄 단위로 읽어서 처리
void handleSerialFromMega() {
  static String line = "";

  while (MegaSerial.available() > 0) {
    char c = MegaSerial.read();

    if (c == '\n' || c == '\r') {
      if (line.length() > 0) {
        line.trim();

        if (line == "CAPTURE") {
          // 메인 컨베이어 인덕터 촬영 요청
          Serial.println("[ESP32] CAPTURE from Mega → publish to MQTT");
          mqttClient.publish(TOPIC_CAPTURE, "{\"msg\":\"1\"}"); // payload는 단순히 "1"로
        }

        line = "";
      }
    } else {
      line += c;
    }
  }
}

// ===================== 온습도 측정 & MQTT publish =====================
void sendThIfDue() {
  unsigned long now = millis();
  if (now - lastThSentMs < TH_SEND_INTERVAL) {
    return; // 아직 1분 안 지남
  }
  lastThSentMs = now;

  // 센서에서 값 읽기
  float temperature = dht.readTemperature();  // 기본: 섭씨
  float humidity    = dht.readHumidity();

  // 읽기 실패한 경우
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("[ESP32] Failed to read from DHT sensor!");
    return;
  }

  // JSON 문자열 생성
  // 예: {"temperature":23.4,"humidity":55.0}
  char payload[80];
  snprintf(payload, sizeof(payload),
           "{\"temperature\":%.2f,\"humidity\":%.2f}",
           temperature, humidity);

  Serial.print("[ESP32] Publish TH: ");
  Serial.println(payload);

  // MQTT publish
  mqttClient.publish(TOPIC_TH, payload);
}




#include <WiFi.h>
#include <WiFiUdp.h>
#include <HardwareSerial.h>

#define BUFSIZE 2048
uint8_t buf[BUFSIZE];
// Set these to your desired credentials.
const char* ssid = "ESP32";  // Enter SSID here
const char* password = "87654321";  //Enter Password here
const char triggerPin = 4;
const int localUDPPort = 58800;
volatile boolean connected = false;
char packetBuffer[255];
HardwareSerial MySerial(2);
WiFiUDP udp;

void connectToWiFi(const char * ssid, const char * pwd){
  Serial.println("Starting WiFi Access Point " + String(ssid));
  //Initiate connection
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, pwd);
  delay(100);
  udp.begin(localUDPPort);
  Serial.println("");
  Serial.print(F("Started AP "));
  Serial.println(ssid);
  Serial.print(F("IP: "));
  // by default, the access point IP address is 192.168.4.1
  Serial.println(WiFi.softAPIP());  
}

void setup() {
  pinMode(triggerPin, OUTPUT);
  digitalWrite(triggerPin, HIGH);  
  Serial.begin(115200);
  Serial.println();
  Serial.println("Configuring access point...");
  connectToWiFi(ssid, password);  //Connect to the WiFi network
  MySerial.begin(1000000, SERIAL_8N1, 16, 17);  // Start the hardware serial to receive audio data
  MySerial.setTimeout(100);
}

void loop() {
  static long long total_bytes = 0;
  static int counter = 0;
  int packetSize = udp.parsePacket();
  if(packetSize){
    int len = udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len] = 0;
    Serial.print("Received(IP/Size/Data): ");
    Serial.print(udp.remoteIP());Serial.print(" / ");
    Serial.print(packetSize);Serial.print(" / ");
    Serial.println(packetBuffer);
    // turn on / off data based on this message
    if(packetBuffer[0] == 0x01){
      connected = 1;
    } else {
      connected = 0;
    }
  }
  
  if(connected){
    // first empty rx buffer
    while(MySerial.available()) MySerial.read();
    digitalWrite(triggerPin, LOW);  // ask for data
    int nb = MySerial.readBytes(buf, BUFSIZE);
    total_bytes += nb;
    if(nb){
      udp.beginPacket(udp.remoteIP(),udp.remotePort());
      udp.write(buf,nb);
      udp.endPacket();
    } 
    
    if(++counter == 100){
      Serial.print("Bytes so far: ");
      Serial.println(total_bytes);
      counter = 0;
    }
  } else {
    digitalWrite(triggerPin, HIGH);  // stop data
    //client.stop();
    if(total_bytes){
      Serial.print("Total bytes: ");
      Serial.println(total_bytes);
      total_bytes = 0;
    }
  }
}

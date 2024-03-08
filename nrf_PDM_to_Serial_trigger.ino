#include <PDM.h>
#define RED 22     
#define BLUE 24     
#define GREEN 23
#define LED_PWR 25
#define LED_Pin A3
#define BUFSIZE 2048
static const char channels = 1;
static const int frequency = 16000;
uint16_t buf[BUFSIZE/2]; // buffer for 16-bit samples
volatile int bytesAvailable = 0;  // Number of audio samples read
volatile int tx_done = 1;
const char triggerPin = 6;  // start on HIGH, end on LOW
int pdm_started = 0;
long long totalBytes = 0;

void onPDMdata(){
  if(tx_done){
    int nbytes = PDM.available();
    PDM.read(buf, nbytes);
    bytesAvailable = nbytes;
  } else {
    Serial.println("Lost data");
  }
}

void setup() {
  digitalWrite(LED_PWR, LOW);
  pinMode(triggerPin, INPUT_PULLUP);
  pinMode(LED_Pin, OUTPUT);
  totalBytes = 0;
  Serial.begin(115200);
  Serial1.begin(0x10000000);
  PDM.setBufferSize(BUFSIZE);
  PDM.onReceive(onPDMdata);
  PDM.setGain(0x01);  // min 0x0, default 0x28, max 0x50  
}

void loop() {
  if(!digitalRead(triggerPin)){
      if(!pdm_started){
        Serial.println("Starting PDM");
        while(!PDM.begin(channels, frequency));
        Serial.println("PDM started");
        bytesAvailable = 0;  // discard what's currently in the buffer
        pdm_started = 1;
      }
      if (bytesAvailable){
        // send buf out via UART
        digitalWrite(LED_Pin,HIGH);
        tx_done = 0;
        /* send data out via Serial1 */
        uint8_t * p = (uint8_t *)&buf[0];
        for(int i=0; i<bytesAvailable; i+=2){
           Serial1.write(*(p+i+1));
           Serial1.write(*(p+i));
        }
        Serial1.flush();
        totalBytes += bytesAvailable;
        bytesAvailable = 0;
        tx_done = 1;
        digitalWrite(LED_Pin,LOW);
      }
  } else {
    if(pdm_started){
      pdm_started = 0;
      PDM.end();
      Serial.println("PDM ended.");
      Serial.print("Total bytes sent: ");
      Serial.println(totalBytes);
      totalBytes = 0;
    }  
  }
}

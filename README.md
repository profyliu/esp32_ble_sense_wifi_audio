# Description

This is a demo project I developed for the IE 6010 course as a core course for the MS in Artificial Intelligence program at Wayne State University.

Course webpage: https://yliu.eng.wayne.edu/teaching/IE5995/index.html

In this project, we create a wireless microphone over WiFi. Specifically, we make use of the WiFi radio on ESP32 and make use of the integrated PDM microphone on the Arduino Nano 33 BLE Sense. 

On Arduino BLE Sense, audio is sampled using the PDM library (which implements a ping-pong buffer so, if processing is fast enough, no data is lost between sampling and processing (i.e., transmitting) tasks) on the BLE Sense, 
and the data is sent to ESP32 via UART at the highest allowable baud rate. 

On ESP32, the audio data is received over UART, and then sent out via UDP packets over WiFi. 


## Installation

Upload ESP32_UART_to_UDP_client_AP.ino via Arduino IDE to the ESP32 board.

Upload nrf_PDM_to_Serial_trigger.ino via Arduino IDE to the Arduino Nano 33 BLE Sense board.

Connect the two boards' UART pins according to the connection.jpg. 

Download the audio_pc_UDP_server.py to the PC. If pyaudio is not installed, use "pip install pyaudio" to install it. 

Power up the two boards separately using their micro-USB ports. 

On the PC, first connect to the WiFi access point published by the ESP32 (see the source code for the SSID and password), then run the python file. 

## Examples

Start listening and save the audio file to ~/Audio/filename.wav, where filename is the timestamp: 

```bash
python audio_pc_UDP_server.py
```

Start listening, play back the audio instantaneously on the PC speaker, but do not save to file:

```bash
python audio_pc_UDP_server.py -p 1 -s 0
```


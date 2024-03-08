# This python script listens on UDP port 58800
import socket
import pyaudio
import wave 
import time
import datetime
import sys
import array
import struct 
from os.path import expanduser
import os
import argparse
import platform    
import subprocess  

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--play", type=int, default=0, help="1: play, 0: not play")
ap.add_argument("-s", "--save", type=int, default=1, help="1: save, 0: not save")
ap.add_argument("-w", "--samplewidth", type=int, default=2, help="2 or 4, bytes")
ap.add_argument("-c", "--channels", type=int, default=1, help="1 or 2")
ap.add_argument("-t", "--timer", type=int, default=7200, help="how many seconds")
ap.add_argument("-r", "--repetitions", type=int, default=1, help="how many repetitions")
ap.add_argument("-m", "--motion_trigger", type=int, default=0, help="0 no, 1 move, 2 move or pir")
ap.add_argument("-l", "--length_per_motion", type=int, default=180, help="how many seconds")
args = vars(ap.parse_args())

home = expanduser("~")
if not os.path.exists(home + "/Audio"):
    os.makedirs(home + "/Audio")
save_dir = home + "/Audio"

PORT = 58800  # Port to listen on (non-privileged ports are > 1023)
chunk = 2048  # chunk size of bytes per recv
sample_rate = 16000  # audio sample rate (should match with the server, 1/2)
sample_width = args['samplewidth']
n_channels = args['channels']
play = args['play']
save = args['save']
timer = args['timer']
repetitions = args['repetitions']
trigger = args['motion_trigger']
length_per_motion = args['length_per_motion']

if n_channels not in [1,2]:
    n_channels = 1
if sample_width not in [2,4]:
    sample_width = 2
if play not in [0,1]:
    play = 1
if save not in [0,1]:
    save = 1
if trigger not in [0,1,2]:
    trigger = 0

print("Sample rate: {:d} | Sample width: {:d} bytes | Channels: {:d} | Play: {:d} | Save: {:d}".format(sample_rate, sample_width, n_channels, play, save))

if trigger == 0:
    total_bytes = 0
    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(2)  # if no data in 5 sec, stop
    except socket.error:
        print('Failed to create socket.')
        sys.exit()
    try:
        s.bind(('', PORT))
    except socket.error:
        print('Bind failed. Error')
        sys.exit()
    print('Server listening')
    
    
    print("Connected. Streaming ...")
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    stream = p.open(format = p.get_format_from_width(sample_width),  # 16-bit
                    channels = n_channels,
                    rate = sample_rate,
                    output = True)  # output=True means that the sound will be played rather than recorded
    
    if n_channels == 2:
        s.sendto(b'\x01\x02', ("192.168.4.1",58800))
    else:
        s.sendto(b'\x01\x01', ("192.168.4.1",58800))
        
    nrep = 0;  # number of repetitions completed
    while(nrep < repetitions):    
        nrep = nrep + 1    
        try:
            if save:
                filename = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S.wav")
            else:
                filename = "tmp.wav"
            f = wave.open(save_dir + "/" + filename, "wb")
            f.setnchannels(n_channels)  # how many microphones
            f.setsampwidth(sample_width)  # n bytes 
            f.setframerate(sample_rate)
            nbytes = 0
            target_bytes = timer*sample_rate*sample_width*n_channels
            while nbytes < target_bytes: 
                try:
                    d = s.recvfrom(chunk)
                except:
                    s.sendto(b'\x00', ("192.168.4.1",58800))
                    break
                data = d[0]
                this_len = len(data)
                nbytes = nbytes + this_len
                total_bytes = total_bytes + this_len
                if play:
                    stream.write(data)
                if save:
                    f.writeframesraw(data)
            f.close()
            if save:
                print("Written file "+str(nrep))
            nbytes = 0
        except KeyboardInterrupt:
            s.sendto(b'\x00', ("192.168.4.1",58800))
            print("Interrupted by user. Disconnected.")
            s.close()
            stream.close()
            p.terminate()
            print("Bytes: {:d} Lengths: {:.1f} s".format(total_bytes, total_bytes/(sample_rate*n_channels*sample_width)))
            if total_bytes < 1000 and save == 1:
                os.remove(save_dir + "/" + filename)
            sys.exit()
            
    s.sendto(b'\x00', ("192.168.4.1",58800))
    print("Disconnected.")
    s.close()
    stream.close()
    p.terminate()
    print("Bytes: {:d} Lengths: {:.1f} s".format(total_bytes, total_bytes/(sample_rate*n_channels*sample_width)))
    if total_bytes < 1000 and save == 1:
        os.remove(save_dir + "/" + filename)
    sys.exit()
else:
    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(2)  # if no data in 5 sec, stop
    except socket.error:
        print('Failed to create socket.')
        sys.exit()
    try:
        s.bind(('', PORT))
    except socket.error:
        print('Bind failed. Error')
        sys.exit()
    print('Server listening for trigger')
    
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    stream = p.open(format = p.get_format_from_width(sample_width),  # 16-bit
                    channels = n_channels,
                    rate = sample_rate,
                    output = True)  # output=True means that the sound will be played rather than recorded
    
    s.sendto(b'\x00', ("192.168.4.1",58800))  
    while True:   
        # empty the rx buffer
        try:
            d = s.recvfrom(chunk)
        except Exception:
            print("rx buffer cleared")

        s.sendto(b'\x00', ("192.168.4.1",58800))
        while True:
            try:
                d = s.recvfrom(1)
                data = int(d[0].decode());
                break
            except KeyboardInterrupt:
                s.sendto(b'\x00', ("192.168.4.1",58800))
                print("Interrupted by user. Disconnected.")
                s.close()
                stream.close()
                p.terminate()
                sys.exit()
            except Exception:
                s.sendto(b'\x00', ("192.168.4.1",58800))
                continue
        print("Triggered level " + str(data) + " at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        total_bytes = 0
        if data <= trigger:        
            if data == 1:
                reason = "Motion_"
            elif data == 2:
                reason = "PIR_"
            else:
                reason = ""
            try:
                if save:
                    filename = reason + datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S") + ".wav"
                else:
                    filename = "tmp.wav"
                f = wave.open(save_dir + "/" + filename, "wb")
                f.setnchannels(n_channels)  # how many microphones
                f.setsampwidth(sample_width)  # n bytes 
                f.setframerate(sample_rate)
                nbytes = 0
                target_bytes = length_per_motion*sample_rate*sample_width*n_channels
                
                if n_channels == 2:
                    s.sendto(b'\x01\x02', ("192.168.4.1",58800))
                else:
                    s.sendto(b'\x01\x01', ("192.168.4.1",58800))
                
                while nbytes < target_bytes: 
                    try:
                        d = s.recvfrom(chunk)
                    except:
                        print("recvfrom timeout")
                        s.sendto(b'\x00', ("192.168.4.1",58800))
                        break
                    data = d[0]
                    this_len = len(data)
                    nbytes = nbytes + this_len
                    total_bytes = total_bytes + this_len
                    if play:
                        stream.write(data)
                    if save:
                        f.writeframesraw(data)
                f.close()
                s.sendto(b'\x00', ("192.168.4.1",58800))
                if save:
                    print("Written " + filename + " " + str(nbytes) + " bytes.")
                nbytes = 0
            except KeyboardInterrupt:
                s.sendto(b'\x00', ("192.168.4.1",58800))
                print("Interrupted by user. Disconnected.")
                s.close()
                stream.close()
                p.terminate()
                print("Bytes: {:d} Lengths: {:.1f} s".format(total_bytes, total_bytes/(sample_rate*n_channels*sample_width)))
                if total_bytes < 1000 and save == 1:
                    os.remove(save_dir + "/" + filename)
                sys.exit()
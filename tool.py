#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎵 VoiceSecret
Record + Embed + Extract secret messages in audio files
Supports WAV, MP3, ACC (any format ffmpeg can handle)
By: Hasnain Dark Net
"""

import os
import subprocess
import wave
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import sys
import time

END_MARKER = "###END###"

# ---------- Terminal Colors ----------
RED = "\033[1;91m"
GREEN = "\033[1;92m"
YELLOW = "\033[1;93m"
CYAN = "\033[1;96m"
MAGENTA = "\033[1;95m"
RESET = "\033[0m"

# ---------- Typing Effect ----------
def type_print(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print("")

# ---------- Big Logo / Banner ----------
def big_banner():
    os.system("clear")
    logo = f"""
{MAGENTA}
 __     ______  _    _   _      ____   _____ ______ 
 \ \   / / __ \| |  | | | |    / __ \ / ____|  ____|
  \ \_/ / |  | | |  | | | |   | |  | | (___ | |__   
   \   /| |  | | |  | | | |   | |  | |\___ \|  __|  
    | | | |__| | |__| | | |___| |__| |____) | |____ 
    |_|  \____/ \____/  |______\____/|_____/|______|
{CYAN}Ultimate Voice Secret Tool
Record + Embed + Extract Hidden Messages
By: Hasnain Dark Net
{RESET}
"""
    type_print(logo, delay=0.0005)
    type_print(f"{YELLOW}=============================================={RESET}\n", 0.001)

# ---------- Recording Function ----------
def record_audio():
    sample_rate = 44100
    channels = 1
    audio_data = []

    type_print(f"{CYAN}🎤 Recording started... Press ENTER to stop.{RESET}")

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_data.append(indata.copy())

    stream = sd.InputStream(samplerate=sample_rate, channels=channels, callback=callback)

    with stream:
        input()
        type_print(f"{YELLOW}⏹ Stopping recording...{RESET}")

    audio_np = np.concatenate(audio_data, axis=0)
    filename = "recorded_audio.wav"
    write(filename, sample_rate, audio_np)
    type_print(f"{GREEN}✅ Recording saved as {filename}{RESET}")
    return filename

# ---------- Convert Any Audio to PCM ----------
def convert_to_pcm(input_file):
    converted_file = "temp_pcm.wav"
    command = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        converted_file
    ]
    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        type_print(f"{RED}❌ Failed to convert {input_file} to PCM. Make sure ffmpeg is installed and the file exists.{RESET}")
        sys.exit(1)
    return converted_file

# ---------- Embed Message ----------
def embed_message(input_file, output_file, message):
    type_print(f"{CYAN}🔄 Converting to PCM...{RESET}")
    pcm_file = convert_to_pcm(input_file)

    with wave.open(pcm_file, 'rb') as audio:
        params = audio.getparams()
        frames = bytearray(audio.readframes(audio.getnframes()))

    message += END_MARKER
    binary = ''.join(format(ord(c), '08b') for c in message)

    if len(binary) > len(frames):
        type_print(f"{RED}❌ Message too long for this audio!{RESET}")
        os.remove(pcm_file)
        return

    for i in range(len(binary)):
        frames[i] = (frames[i] & 254) | int(binary[i])

    with wave.open(output_file, 'wb') as modified:
        modified.setparams(params)
        modified.writeframes(frames)

    os.remove(pcm_file)
    type_print(f"{GREEN}✅ Message Embedded Successfully into {output_file}{RESET}")

# ---------- Extract Message ----------
def extract_message(input_file):
    type_print(f"{CYAN}🔄 Converting to PCM...{RESET}")
    pcm_file = convert_to_pcm(input_file)

    with wave.open(pcm_file, 'rb') as audio:
        frames = bytearray(audio.readframes(audio.getnframes()))

    bits = [str(frames[i] & 1) for i in range(len(frames))]
    binary = ''.join(bits)

    chars = [chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8)]
    decoded = ''.join(chars)

    os.remove(pcm_file)

    if END_MARKER in decoded:
        message = decoded.split(END_MARKER)[0]
        type_print(f"{GREEN}💌 Secret Message: {message}{RESET}")
    else:
        type_print(f"{RED}❌ No hidden message found!{RESET}")

# ---------- Main Function ----------
def main():
    big_banner()

    record_option = input(f"{CYAN}🎤 Record new voice? (y/n): {RESET}").lower()
    if record_option == "y":
        input_audio = record_audio()
    elif record_option == "n":
        input_audio = input(f"{CYAN}Enter existing audio file path: {RESET}")
        if not os.path.exists(input_audio):
            type_print(f"{RED}❌ File does not exist! Exiting...{RESET}")
            sys.exit(1)
    else:
        type_print(f"{RED}❌ Invalid option! Exiting...{RESET}")
        sys.exit(1)

    type_print(f"""
{YELLOW}1️⃣ Embed Message
2️⃣ Extract Message{RESET}
""")
    choice = input(f"{CYAN}Choose (1 or 2): {RESET}")

    if choice == "1":
        output_file = input(f"{CYAN}Enter output WAV file name: {RESET}")
        secret_msg = input(f"{CYAN}Enter secret message: {RESET}")
        embed_message(input_audio, output_file, secret_msg)
    elif choice == "2":
        extract_message(input_audio)
    else:
        type_print(f"{RED}❌ Invalid choice! Exiting...{RESET}")

if __name__ == "__main__":
    main()

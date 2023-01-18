import os.path

import espeakng # TTS
import whisper # ARS

# for recording
import sounddevice as sd 
from scipy.io.wavfile import write

# TTS Configuration
mySpeaker = espeakng.Speaker()
mySpeaker.voice = 'it'
mySpeaker.pitch = 120
mySpeaker.wpm = 140
mySpeaker.say('Hola, como estas?', wait4prev=True)

# This is ofr waiting until the text finishes
# mySpeaker.say('I am a demo of the say() method.', wait4prev=True)

fs = 44100  # Sample rate
seconds = 3  # Duration of recording

myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
print('Recording...')
sd.wait()  # Wait until recording is finished
print('Recording finished.')
write('output.wav', fs, myrecording)  # Save as WAV file 


# EXMAPLE DETECTING LANGUAGE 
# whisper.detect_language() and whisper.decode() which provide
# lower-level access to the model.

model = whisper.load_model("base")

# load audio and pad/trim it to fit 30 seconds
audio = whisper.load_audio("output.wav") # also works with wav
audio = whisper.pad_or_trim(audio)

# make log-Mel spectrogram and move to the same device as the model
mel = whisper.log_mel_spectrogram(audio).to(model.device)

# detect the spoken language
_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")

# decode the audio
options = whisper.DecodingOptions(fp16 = False) # when runing in CPU (p16 = False)
result = whisper.decode(model, mel, options)

# print the recognized text
print(result.text)

if 'bien' in result.text:
    print('me alegro mucho!')
    mySpeaker.say('me alegro mucho!', wait4prev=True)
elif 'mal' in result.text:
    print('vaya...')
    mySpeaker.say('vaya...', wait4prev=True)
else:
    print('aham')
    mySpeaker.say('aham', wait4prev=True)

print('bueno, me tengo que ir, adios.')
mySpeaker.say('bueno, me tengo que ir, adios.', wait4prev=True)
print('end of interaction')



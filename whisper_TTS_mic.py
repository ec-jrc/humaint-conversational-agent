#!python
import whisper
import speech_recognition as sr
import torch
import numpy as np

print("loading model")

model = whisper.load_model("tiny.en")

print("model loaded")

r = sr.Recognizer()
mic = sr.Microphone()

with mic as source:
    audio = r.listen(source)
    print("Say someth")
    while(len(audio.get_raw_data()) < 1839680):
        audio = r.listen(source)
    print(len(audio.get_raw_data()))

torch_audio = torch.from_numpy(np.frombuffer(audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)
audio_data = torch_audio
result = model.transcribe(audio_data,language='english')
print("You said: " + result["text"])
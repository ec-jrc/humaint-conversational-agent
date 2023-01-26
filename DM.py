import os.path
import whisper


# # BASIC EXMAPLE
# model = whisper.load_model("base")
# result = model.transcribe("ASR/test1_en.mp3", fp16 = False)
# print(result["text"])


# EXMAPLE DETECTING LANGUAGE 
# whisper.detect_language() and whisper.decode() which provide
# lower-level access to the model.

model = whisper.load_model("base")

# load audio and pad/trim it to fit 30 seconds
audio = whisper.load_audio("ASR/test1_en.mp3") # also works with wav
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

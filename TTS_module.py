#!python
import espeakng
import json

CONFIG_PATH = "config.json"
with open(CONFIG_PATH, 'r', encoding='utf-8') as config:
    configs = json.load(config)

speaker_voice = configs['SPEAKER_VOICE']

def Say(text):
    new_speaker = espeakng.Speaker()
    new_speaker.voice = speaker_voice
    new_speaker.say(text)

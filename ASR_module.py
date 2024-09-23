import sys
import sounddevice as sd
import numpy as np
#import whisper
from faster_whisper import WhisperModel
import asyncio
import json
from difflib import SequenceMatcher
import string
import new_dialogmodule as new_dm
import queue

# SETTINGS
CONFIG_PATH = "config.json"
with open(CONFIG_PATH, 'r', encoding='utf-8') as config:
    configs = json.load(config)
WHISPER_MODEL = configs['WHISPER_MODEL']
LANGUAGE = configs['LANGUAGE']
BLOCKSIZE = configs['AUDIO_INTERVALS'] * 16000 # The size of the audio block. blocksize / 16000 = Length of the audio in seconds.
WHISPER_MAX_BLOCKSIZE = configs['WHISPER_MAX_TIME'] * 16000 # The size of the biggest audio chunk that can be sent to whisper recognition (MAX 30s)
ALLOWED_SILENCE_TIME = configs['ALLOWED_SILENCE_TIME_CONVERSATION'] # The number of seconds the system keeps listening while in silence
ALLOWED_SILENCE_TIME_CHECK = configs['ALLOWED_SILENCE_TIME_FOR_CHECK'] # The number of seconds the system keeps listening while in silence on check mode
SILENCE_THRESHOLD = configs['SILENCE_THRESHOLD'] # The threshold to consider data as silence
SILENCE_RATIO = configs['SILENCE_RATIO'] # Ratio of silence/no-silence in audio chunk
AMBIENCE_LEVEL_VOLUME = configs['AMBIENCE_LEVEL'] # Defaulted to 5%, but is edited after check
ACCURACY_CHECK_SENTENCE = configs["ACCURACY_CHECK_SENTENCE_ES"] if LANGUAGE == "es" else configs["ACCURACY_CHECK_SENTENCE_IT"]
SOUND_SCALE_MAX_VALUE = configs["SOUND_SCALE_MAX_VALUE"]

# Sentences that whisper default to on silence threshold exceeded
WHISPER_DEFAULT_SENTENCES = {
    "es": [
        "subtítulos por la comunidad de amaraorg",
        "y nos vemos en el próximo vídeo.",
        "¡suscríbete!",
        "¡adiós!",
        "¡hasta la próxima!",
        "www.mooji.org",
        "¡gracias por ver el vídeo",
        "¡gracias por ver el vídeo!",
        "¡suscribete al canal!",
        
    ],
    "it": [
        "alla prossima!",
        "sottotitoli a cura di qtss",
        "sottotitoli e revisione a cura di qtss",
        "sottotitoli a cura di qt",
        "sottotitoli a cura di sottotitoli"
    ]
}

whisper_indata = np.empty([1, 0])
counter = 0
accuracy_checked = False
ambience_level_checked = False
ambience_level_values_array = []

global_ndarray = None
#model = whisper.load_model(WHISPER_MODEL)
#whisper.DecodingOptions(fp16=False)
model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
transcription_result = ""
transcription_paused = False
whisper_random_sentence_solved = False
already_retried = False

async def inputstream_generator(conversation_file):
    """Generator that yields blocks of input data as NumPy arrays."""
    q_in = asyncio.Queue()
    loop = asyncio.get_event_loop()
    def callback(indata, frame_count, time_info, status):
        global whisper_indata, counter
        current_allowed_silence_time = ALLOWED_SILENCE_TIME
        volume_norm = np.linalg.norm(indata) # We check volume level in order to check if there is silence
        volume_percent = round(int(volume_norm) / SOUND_SCALE_MAX_VALUE * 100)
        '''bar_string = "|" * multiplier
        print(bar_string + " " + str(multiplier) + "%") #This print shows volume level visually'''
        if volume_percent <= AMBIENCE_LEVEL_VOLUME: # Empirically checked, 40 000 is ambience audio level.
            counter += 1
            if not ambience_level_checked:# Still on pre-execution check of ambience_level
                print("Silence detected for " + str(counter) + "s")
                new_dm.write_to_conversation_file("Silence detected for " + str(counter) + "s", conversation_file, "System")
                ambience_level_values_array.append(volume_percent)
                current_allowed_silence_time = ALLOWED_SILENCE_TIME_CHECK
        if not transcription_paused and (volume_percent > AMBIENCE_LEVEL_VOLUME or not ambience_level_checked):
            whisper_indata = np.append(whisper_indata, indata) # Appending 1s chunks to whisper array

        # Check whether max whisper blocksize has been reached or there are too many silent chunks
        if whisper_indata.size >= WHISPER_MAX_BLOCKSIZE or counter >= current_allowed_silence_time:
            counter = 0
            loop.call_soon_threadsafe(q_in.put_nowait, (whisper_indata.copy(), status))
            whisper_indata = np.empty([1, 0])

    stream = sd.InputStream(samplerate=16000, channels=1, dtype='int16', blocksize=BLOCKSIZE, callback=callback)
    with stream:
        while True:
            if not transcription_paused:
                indata, status = await q_in.get()
                yield indata, status


async def process_input_audio(conversation_file, config_json_file):
    global global_ndarray, accuracy_checked, transcription_paused, whisper_random_sentence_solved, already_retried
    times_checked = 0
    async for inputdata, status in inputstream_generator(conversation_file):
        indata_flattened = abs(inputdata.flatten())

        # discard buffers that contain mostly silence
        if (np.asarray(np.where(indata_flattened > SILENCE_THRESHOLD)).size < SILENCE_RATIO):
            if not ambience_level_checked:  # Still on pre-execution check of ambience level
                set_new_ambience_level(np.mean(indata_flattened), conversation_file)
            continue

        if (global_ndarray is not None):
            global_ndarray = np.concatenate((global_ndarray, inputdata), dtype='int16')
        else:
            global_ndarray = inputdata

        inputdata_transformed = global_ndarray.flatten().astype(np.float32) / 32768.0
        segments, info = model.transcribe(inputdata_transformed, language=LANGUAGE)
        result = ""
        for segment in segments:
            result += segment.text
        global_ndarray = None
        if accuracy_checked and ambience_level_checked:# Once accuracy and ambience level have been checked, experiment can begin
            if result.startswith(" "):
                result = result[1:]
            if result.lower() in WHISPER_DEFAULT_SENTENCES[LANGUAGE]:
                if not whisper_random_sentence_solved:
                    if not already_retried:
                        already_retried = True
                        retry_vocally = input("\nDetected whisper default sentence. Activate manual input? (yes/no): ")
                        if retry_vocally == "no":
                            pause_recognition(False)
                            print("Speak now: ")
                            result = ""
                            new_dm.sum_not_understood("not-understood", LANGUAGE, config_file=config_json_file)
                            continue
                        else:
                            result = input("\nPlease enter manually what user said: ")
                            new_dm.sum_not_understood("not-understood", LANGUAGE, config_file=config_json_file)
                            set_whisper_random_sentence_solved(True)
                    else:
                        already_retried = False
                        continue
                else:
                    continue
            set_transcription_result(result)
            result = result.translate(str.maketrans('', '', string.punctuation))
            new_dm.sum_more_info_request(result.lower(), LANGUAGE, config_json_file)
            new_dm.sum_request_repeat(result.lower(), LANGUAGE, config_json_file)
        else:
            [accuracy, wp_result, times_checked] = check_accuracy(result, conversation_file, times_checked)
            json_data = {}
            with open("user_config_files/" + config_json_file, "r", encoding="utf-8") as config_f:
                json_data = json.load(config_f)
                if times_checked < 2:
                    accuracy_ptg_string = "accuracy_ptg_1"
                    accuracy_sentence_detected_string = "accuracy_sentence_detected_1"
                else:
                    accuracy_ptg_string = "accuracy_ptg_2"
                    accuracy_sentence_detected_string = "accuracy_sentence_detected_2"
                json_data[accuracy_ptg_string] = accuracy
                json_data[accuracy_sentence_detected_string] = wp_result
                config_f.close()
            with open("user_config_files/" + config_json_file, "w", encoding="utf-8") as config_f:
                json.dump(json_data, config_f, indent=4)
                config_f.close()

def set_transcription_result(result):
    global transcription_result
    transcription_result = result

def check_accuracy(whisper_result, conversation_file, times_checked):
    global accuracy_checked, ACCURACY_CHECK_SENTENCE

    # Removing punctuation
    ACCURACY_CHECK_SENTENCE = ACCURACY_CHECK_SENTENCE.translate(str.maketrans('','',string.punctuation))
    whisper_result = whisper_result.translate(str.maketrans('', '', string.punctuation))

    if whisper_result.startswith(" "):
        whisper_result = whisper_result[1:]

    accuracy = np.round(SequenceMatcher(None, ACCURACY_CHECK_SENTENCE.lower(), whisper_result.lower()).ratio() * 100)
    print("User: " + whisper_result)
    new_dm.write_to_conversation_file(whisper_result, conversation_file, "User")
    print("Accuracy ratio is " + str(accuracy) + "%")
    new_dm.write_to_conversation_file("Accuracy ratio is " + str(accuracy) + "%", conversation_file, "System")
    times_checked += 1
    if times_checked >= 2:
        accuracy_checked = True
    else:
        print("System: Go ahead once more!")
        new_dm.write_to_conversation_file("Go ahead once more!", conversation_file, "System")
    return [accuracy, whisper_result, times_checked]

def set_new_ambience_level(indata_mean, conversation_file):
    global ambience_level_values_array, ambience_level_checked, AMBIENCE_LEVEL_VOLUME, SILENCE_THRESHOLD
    ambience_level_mean = np.mean(ambience_level_values_array)
    print("New ambience level noise detected. Updating value...")
    new_dm.write_to_conversation_file("New ambience level noise detected. Updating value...", conversation_file, "System")
    AMBIENCE_LEVEL_VOLUME = ambience_level_mean
    SILENCE_THRESHOLD = int(indata_mean + 10) # Adding 10 units of tolerance
    ambience_level_checked = True
    print("CHECK 2: Say out loud the template sentence.")
    new_dm.write_to_conversation_file("CHECK 2: Say out loud the template sentence.", conversation_file, "System")

def pause_recognition(pause):
    global transcription_paused, global_ndarray, whisper_indata
    transcription_paused = pause
    global_ndarray = None
    whisper_indata = np.empty([1, 0])

def set_whisper_random_sentence_solved(solved):
    global whisper_random_sentence_solved
    whisper_random_sentence_solved = solved


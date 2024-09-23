import sounddevice as sd
import numpy as np
import whisper
import asyncio
import json

# SETTINGS
CONFIG_PATH = "config.json"
with open(CONFIG_PATH, 'r', encoding='utf-8') as config:
    configs = json.load(config)
WHISPER_MODEL = configs['WHISPER_MODEL']
LANGUAGE = configs['LANGUAGE']
BLOCKSIZE = configs['AUDIO_INTERVALS'] * 16000 # The size of the audio block. blocksize / 16000 = Length of the audio in seconds.
WHISPER_MAX_BLOCKSIZE = configs['WHISPER_MAX_TIME'] * 16000 # The size of the biggest audio chunk that can be sent to whisper recognition (MAX 30s)
ALLOWED_SILENCE_TIME = configs['ALLOWED_SILENCE_TIME'] # The number of seconds the system keeps listening while in silence
SILENCE_THRESHOLD = configs['SILENCE_THRESHOLD'] # The threshold to consider data as silence
SILENCE_RATIO = configs['SILENCE_RATIO'] # Ratio of silence/no-silence in audio chunk

whisper_indata = np.empty([1, 0])
counter = 0

global_ndarray = None
model = whisper.load_model(WHISPER_MODEL)
whisper.DecodingOptions(fp16=False)
transcription_result = ""

async def inputstream_generator():
    """Generator that yields blocks of input data as NumPy arrays."""
    q_in = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def callback(indata, frame_count, time_info, status):
        global whisper_indata, counter
        volume_norm = np.linalg.norm(indata) # We check volume level in order to check if there is silence
        #print("|" * int(volume_norm) + str(round(volume_norm))) #This print shows volume level visually
        if round(volume_norm) <= 40000: # Empirically checked, 40 000 is ambience audio level.
            counter += 1
            print("Silence detected for " + str(counter) + "s")
        whisper_indata = np.append(whisper_indata, indata) # Appending 1s chunks to whisper array

        # Check whether max whisper blocksize has been reached or there are too many silent chunks
        if whisper_indata.size >= WHISPER_MAX_BLOCKSIZE or counter >= ALLOWED_SILENCE_TIME:
            if counter >= ALLOWED_SILENCE_TIME:
                print("Exceeded silence threshold, sending data to whisper")
            counter = 0
            loop.call_soon_threadsafe(q_in.put_nowait, (whisper_indata.copy(), status))
            whisper_indata = np.empty([1, 0])

    stream = sd.InputStream(samplerate=16000, channels=1, dtype='int16', blocksize=BLOCKSIZE, callback=callback)
    with stream:
        while True:
            indata, status = await q_in.get()
            yield indata, status


async def process_input_audio():
    #print("Processing audio buffer")
    global global_ndarray
    async for inputdata, status in inputstream_generator():
        indata_flattened = abs(inputdata.flatten())

        # discard buffers that contain mostly silence
        if (np.asarray(np.where(indata_flattened > SILENCE_THRESHOLD)).size < SILENCE_RATIO):
            continue

        if (global_ndarray is not None):
            global_ndarray = np.concatenate((global_ndarray, inputdata), dtype='int16')
        else:
            global_ndarray = inputdata

        inputdata_transformed = global_ndarray.flatten().astype(np.float32) / 32768.0
        result = model.transcribe(inputdata_transformed, language=LANGUAGE)
        global_ndarray = None
        set_transcription_result(result['text'])

def set_transcription_result(result):
    global transcription_result
    transcription_result = result


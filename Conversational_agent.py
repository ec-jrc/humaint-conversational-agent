import sys
import sounddevice as sd
import numpy as np
import whisper
import asyncio
import json
import queue

# SETTINGS
CONFIG_PATH = "config.json"
with open(CONFIG_PATH, 'r', encoding='utf-8') as config:
    configs = json.load(config)
WHISPER_MODEL = configs['WHISPER_MODEL']
LANGUAGE = configs['LANGUAGE']
BLOCKSIZE = configs['BLOCKSIZE'] # The size of the audio block. blocksize / 16000 = Length of the audio in seconds.
SILENCE_THRESHOLD = configs['SILENCE_THRESHOLD'] # The threshold to consider data as silence
SILENCE_RATIO = configs['SILENCE_RATIO'] # Ratio of silence/no-silence in audio chunk

global_ndarray = None
model = whisper.load_model(WHISPER_MODEL)
whisper.DecodingOptions(fp16=False)

async def inputstream_generator():
    """Generator that yields blocks of input data as NumPy arrays."""
    q_in = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))

    stream = sd.InputStream(samplerate=16000, channels=1, dtype='int16', blocksize=BLOCKSIZE, callback=callback)
    with stream:
        while True:
            indata, status = await q_in.get()
            yield indata, status


async def process_input_audio():
    print("Processing audio buffer")
    global global_ndarray
    async for inputdata, status in inputstream_generator():

        if (global_ndarray is not None):
            global_ndarray = np.concatenate((global_ndarray, inputdata), dtype='int16')
        else:
            global_ndarray = inputdata

        inputdata_transformed = global_ndarray.flatten().astype(np.float32) / 32768.0
        result = model.transcribe(inputdata_transformed, language=LANGUAGE)
        global_ndarray = None
        print(result["text"])

async def main():
    print('\nActivating wire ...\n')
    listener_task = asyncio.create_task(process_input_audio())

    while True:
        await asyncio.sleep(1)

    listener_task.cancel()

    try:
        await audio_task
    except asyncio.CancelledError:
        print('\nwire was cancelled')


if __name__ == "__main__":
    #test_arg = str(sys.argv[1])
    #main(test_arg)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit('\nInterrupted by user')
import sys
import asyncio
import live_transcriber as lt
import chatgpt_bridge as gpt


async def main():
    print('\nStarting listener\n')
    listener_task = asyncio.create_task(lt.process_input_audio())

    while True:
        await asyncio.sleep(1)
        trans_res = lt.transcription_result
        if trans_res != "":
            print(trans_res)
            gpt.process_request(trans_res)
            lt.set_transcription_result("")

    listener_task.cancel()

    try:
        await audio_task
    except asyncio.CancelledError:
        print('\nWhisper not listening anymore')


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit('\nInterrupted by user')
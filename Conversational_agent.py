import sys
import asyncio
import ASR_module as asr
import datetime
import json
import chatgpt_bridge as gpt

async def main():
    global conversation_file_name, config_json_file
    id = input("Enter user id: ")
    print("Creating user files...")
    date_now = datetime.datetime.now()

    timestamp_id = date_now.strftime("%d") + "-" + date_now.strftime("%m") + "-" + \
                   date_now.strftime("%H") + "-" + date_now.strftime("%M") + "-" + id
    conversation_file_name = timestamp_id + ".txt"

    # Creating conversation_file
    with open("conversation_files/" + conversation_file_name, "w",encoding="utf-8") as conv_f:
        pass

    # Creating config_file
    init_conf_json = {"id": id, "accuracy": "", "conversation_file": conversation_file_name}
    config_json_file = timestamp_id + ".json"
    with open("user_config_files/" + timestamp_id + ".json", "w", encoding="utf-8") as conf_f:
        json.dump(init_conf_json, conf_f, indent=4)
        conf_f.close()
    print('\nStarting listener\n')
    listener_task = asyncio.create_task(asr.process_input_audio(conversation_file_name, config_json_file))

    while True:
        await asyncio.sleep(1)
        trans_res = asr.transcription_result
        if trans_res != "":
            user_res = "User: " + trans_res
            print(user_res)
            #gpt.process_request(trans_res, conversation_file_name)
            asr.set_transcription_result("")

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
import openai
import os
import tiktoken
import TTS_module as tts
import json

# Replace YOUR_API_KEY with your OpenAI API key
openai.api_key = os.environ['HUMAINT_CHATGPT_API_KEY']

CONFIG_PATH = "config.json"
with open(CONFIG_PATH, 'r', encoding='utf-8') as config:
    configs = json.load(config)
# Set the model and prompt
CHATGPT_MODEL = configs['CHATGPT_MODEL']
CHATGPT_MAX_TOKENS = configs['CHATGPT_MAX_TOKENS']
TIKTOKEN_ENCODING = tiktoken.encoding_for_model(CHATGPT_MODEL)
messages_list = [{"role": "system", "content": "You are a helpful assistant."}]

# Set the maximum number of tokens to generate in the response
max_tokens = 1024

def process_request(prompt, conversation_file_name):
    prompt_message = {"role": "user", "content": prompt}
    messages_list.append(prompt_message)
    if is_token_size_compliant():
        purge_message_list()

    response = openai.ChatCompletion.create(
        model=CHATGPT_MODEL,
        messages=messages_list
    )
    response_message = {"role": "assistant", "content": response['choices'][0]['message']['content']}
    messages_list.append(response_message)

    user_res = "User: " + messages_list[len(messages_list) - 1]
    assistant_res = "Assistant: " + response['choices'][0]['message']['content']
    print(assistant_res)
    with open("conversation_files/" + conversation_file_name, "a", encoding="utf-8") as conv_f:
        conv_f.write(user_res + "\n")
        conv_f.write(assistant_res + "\n")
        conv_f.close()
    #tts.Say(response['choices'][0]['message']['content'])
    return response['choices'][0]['message']['content']



def is_token_size_compliant():
    num_tokens = 0
    for message in messages_list:
        num_tokens += len(TIKTOKEN_ENCODING.encode(message['content']))

    return num_tokens > CHATGPT_MAX_TOKENS

def purge_message_list():
    #Delete messages 1 and 2 (message 2 becomes 1 after deleting message 1)
    del messages_list[1]
    del messages_list[1]

import openai
import os
import time
import TTS_module as tts

# Replace YOUR_API_KEY with your OpenAI API key
openai.api_key = os.environ['HUMAINT_CHATGPT_API_KEY']

# Set the model and prompt
model_engine = "text-davinci-003"
completion = ""

# Set the maximum number of tokens to generate in the response
max_tokens = 1024

def process_request(prompt):
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    print(completion.choices[0].text)
    tts.Say(completion.choices[0].text)

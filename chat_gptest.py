import openai
import os
import time


# Replace YOUR_API_KEY with your OpenAI API key
openai.api_key = os.environ['HUMAINT_CHATGPT_API_KEY']

# Set the model and prompt
model_engine = "text-davinci-003"
prompt = "create a story"

# Set the maximum number of tokens to generate in the response
max_tokens = 1024

while True:
    try:
        print("Let's do it!")
        # Generate a response
        completion = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    except openai.error.RateLimitError:
        print("Sleeping for 65 secs...")
        time.sleep(65)
        continue

print(completion.choices[0].text)

from openai import OpenAI
import json
import random
import time

# Return an OpenAI client
def get_openai_client():
    keys_filename = '../utils/openai_keys.json'
    with open(keys_filename) as f:
        # Choose a random key from the provided keys
        keys = json.load(f)
        rand_key = random.choice(keys)
        return OpenAI(api_key=rand_key['api_key'])
    
def call_gpt(openai_client, messages, model='gpt-4o', max_retry=10, response_format=None):
    retry_times = 0
    while True:
        try:
            openai_response = openai_client.chat.completions.create(
                model=model, 
                messages=messages,
                response_format=response_format
            )

            return openai_response.choices[0].message.content

        except Exception as e:
            print(f'Error occurred calling GPT, retrying. Error type: {type(e).__name__}')

            if type(e).__name__ == 'RateLimitError':
                time.sleep(10)

            elif type(e).__name__ == 'APIError':
                time.sleep(15)

            elif type(e).__name__ == 'InvalidRequestError':
                return "{}"

            else:
                return "{}"

        retry_times += 1
        if retry_times == max_retry:
            print('Retrying too many times')
            return "{}"
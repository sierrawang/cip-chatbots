import csv
import json
from tqdm import tqdm
from system_prompt import SYSTEM_PROMPT

import sys
sys.path.insert(1, '../helpers')
from chat_usage_helpers import get_sent_message, get_chat_messages
from openai_helper import get_openai_client, call_gpt

def get_conversations_for_user(user_id, chat_messages):
    # Filter to get this user's messages collection
    user_messages = chat_messages[chat_messages['user_id'] == user_id]

    # Add a contextId column to the chat_messages, combining lessonId and assnId
    user_messages = user_messages.assign(contextId=user_messages['lessonId'].fillna(user_messages['assnId']))

    # Sort messages by contextId and then by timestamp within each context
    user_messages = user_messages.sort_values(by=['contextId', 'timestamp'])

    # Group the messages by contextId
    conversations = user_messages.groupby('contextId')

    return conversations

# Format the chat conversation into a string of the form:
# chatbot_message_1: <chatbot_message_1>
# user_message_1: <user_message_1>
# chatbot_message_2: <chatbot_message_2>
# user_message_2: <user_message_2>
def format_chat_conversation(chat_conversation):
    chat_conversation_str = ""
    output_format_str = "{\n"
    
    i = 1
    for _, row in chat_conversation.iterrows():
        if row['authorId'] == 'ai':
            chat_conversation_str += f"chatbot_message_{i}: {row['message']}\n\n"
        else:
            chat_conversation_str += f"user_message_{i}: {row['message']}\n\n"
            output_format_str += f'    "user_message_{i}": {{"message": "{row["message"]}", "classification": ""}},\n'
            i += 1

    # Replace all double quotes with single quotes
    chat_conversation_str = chat_conversation_str.replace('"', "'")

    output_format_str = output_format_str.replace('"', "'")
    output_format_str = output_format_str[:-2] + "\n}"

    return chat_conversation_str, output_format_str

def classify_conversation_chunk(chat_conversation_str, output_format_str, openai_client):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + output_format_str },
        {"role": "user", "content": chat_conversation_str}
    ]
    res = call_gpt(openai_client, messages, response_format={ "type": "json_object" })
    return res

def write_chunk_results(chunk_results_str, conversation_chunk, writer):
    chunk_results = json.loads(chunk_results_str)

    # Index of the user message in the conversation
    user_message_num = 1
    for index, row in conversation_chunk.iterrows():
        if row['authorId'] == 'ai':
            continue
        else:
            # Parse the results
            messageId = row['messageId']
            message = row['message']
            gpt_classification = ""
            try:
                gpt_classification = chunk_results[f"user_message_{user_message_num}"]["classification"]
            except:
                gpt_classification = "ERROR"
            
            row = { 'messageId': messageId, 'message': message, 'classification': gpt_classification }
            # print(row)
            writer.writerow(row)

            # Increment the user message number
            user_message_num += 1

def classify_conversation(chat_conversation, writer, openai_client, chunk_size=20):
    # Ensure that the messages are sorted by timestamp
    chat_conversation = chat_conversation.sort_values(by='timestamp')

    # Divide the conversation into chunks 
    num_messages = len(chat_conversation)
    num_chunks = num_messages // chunk_size
    if num_messages % chunk_size != 0:
        num_chunks += 1

    # Loop through each chunk
    for i in range(num_chunks):
        # Get the start and end indices of this chunk
        start = i * chunk_size
        end = min((i + 1) * chunk_size, num_messages)

        # Classify the messages in this chunk
        conversation_chunk = chat_conversation.iloc[start:end]
        conversation_chunk_str, output_format_str = format_chat_conversation(conversation_chunk)
        chunk_results_str = classify_conversation_chunk(conversation_chunk_str, output_format_str, openai_client)
        write_chunk_results(chunk_results_str, conversation_chunk, writer)

# Output a csv containing the message classifications
# Each row contains the messageId, the message content, and the message classification
def classify(output_filename='../parsed_data/message_classifications.csv'):
    # Load the users who sent messages
    users_sent_messages = get_sent_message()
    user_ids = users_sent_messages['user_id'].unique()

    # Load the chat messages
    chat_messages = get_chat_messages()

    # Define the output file
    output_fieldnames = ['messageId', 'message', 'classification']

    # Open the output file for writing
    with open(output_filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()

        # Loop through each user who send a message
        for i in tqdm(range(len(user_ids)), total=len(user_ids), desc='Classifying messages'):
            # Get the conversations for this user
            user_conversations = get_conversations_for_user(user_ids[i], chat_messages)

            # Get an OpenAI client
            openai_client = get_openai_client()

            # Classify each conversation
            for context_id, chat_conversation in user_conversations:
                classify_conversation(chat_conversation, writer, openai_client)

if __name__ == "__main__":
    classify()
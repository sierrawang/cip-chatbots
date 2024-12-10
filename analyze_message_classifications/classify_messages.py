import csv
import json
import os
import pandas as pd

import sys
sys.path.insert(1, '../utils')
from openai_client import call_gpt

sys.path.insert(1, '../helpers')
from rosters_helpers import get_experiment_roster
from chat_usage_helpers import get_sent_message, get_chat_messages

def init_output_file(output_filename, fieldnames):
    # Open the output file in append mode
    output_file = open(output_filename, 'a', newline='')

    output_writer = csv.writer(output_file)

    # Write the fieldnames to the output file if it is empty
    if os.stat(output_filename).st_size == 0:
        output_writer.writerow(fieldnames)

    return output_file, output_writer

# Return the chat conversations for a user, sorted by timestamp and grouped by contextId
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

# Return True if the user never sent a message in this conversation, False if they did
def never_sent_message(chat_conversation, user_id):
    for index,row in chat_conversation.iterrows():
        if row['authorId'] == user_id:
            return False
    return True

# Return True if the messages in this conversation have already been classified, False otherwise
def was_already_classified(chat_conversation, classified_messages):
    for index, row in chat_conversation.iterrows():
        # Return false if there is a user message that has not been classified
        if not (row['authorId'] == 'ai' or row['messageId'] in classified_messages['messageId'].values):
            return False
        
    # Return true if all user messages have been classified
    return True

# Parse the chat conversation into a string
def parse_chat_conversation(chat_conversation):
    chat_conversation_str = ""
    i = 1

    for index, row in chat_conversation.iterrows():
        if row['authorId'] == 'ai':
            chat_conversation_str += f"chatbot_message_{i}: {row['message']}\n\n"
        else:
            chat_conversation_str += f"user_message_{i}: {row['message']}\n\n"
            i += 1

    # Replace all double quotes with single quotes
    chat_conversation_str = chat_conversation_str.replace('"', "'")

    return chat_conversation_str

def call_gpt_helper(chat_conversation):
    messages = [
        {"role": "system", "content": """A student in an introductory computer science course had the following conversation with a chatbot. Classify each message as one of the following categories:
         
CONCEPTUAL: The message is a question about a concept in computer science.
HOMEWORK: The message is a question about how to solve a specific assignment problem. In this case, the student is typically asking the chatbot to write code for them.
AI: The message is a question about artificial intelligence. In this case, the student is typically asking the chatbot whether it is an AI.
GREETING: The message is a greeting like hello or hi.
GRATITUDE: The message is an expression of gratitude.
OTHER: The message does not fit into any of the above categories.

Output a JSON object with the following format:
{
    "user_message_1": {
            "message": "",
            "classification": ""
        },
    "user_message_2": {
            "message": "",
            "classification": ""
        },
    "user_message_3": {
            "message": "",
            "classification": ""
        },
    ...
}
         
Remember to only output a JSON object! Do NOT respond with any other text."""},
        {"role": "user", "content": chat_conversation}
    ]
    res = call_gpt(messages)
    return res

# Write the gpt generated classifications to the output file
def write_results(conversation_chunk, gpt_result, output_writer):
    # Index of the user message in the conversation
    user_message_num = 1
    for index, row in conversation_chunk.iterrows():
        if row['authorId'] == 'ai':
            continue
        else:
            # Parse the results
            messageId = row['messageId']
            message = row['message']
            gpt_classification = gpt_result[f"user_message_{user_message_num}"]["classification"]
            output_writer.writerow([messageId, message, gpt_classification])

            # Increment the user message number
            user_message_num += 1

# Classify the messages in this conversation and write the results to the output file
def classify_messages_helper(user_id, context_id, chat_conversation, output_writer, 
                             errors_writer, chunk_size, classified_messages):

    # Ensure that the messages are sorted by timestamp
    chat_conversation = chat_conversation.sort_values(by='timestamp')

    # Divide the conversation into chunks 
    num_messages = len(chat_conversation)
    num_chunks = num_messages // chunk_size
    if num_messages % chunk_size != 0:
        num_chunks += 1

    # Loop through each chunk
    num_chunks_classified = 0
    num_chunks_failed = 0
    for i in range(num_chunks):
        # Get the start and end indices of this chunk
        start = i * chunk_size
        end = min((i + 1) * chunk_size, num_messages)

        # Classify the messages in this chunk
        conversation_chunk = chat_conversation.iloc[start:end]

        # If the user never sent a message in this chunk, skip
        if never_sent_message(conversation_chunk, user_id):
            continue

        # If the messages in this chunk have already been classified, skip
        if was_already_classified(conversation_chunk, classified_messages):
            continue

        try:
            conversation_str = parse_chat_conversation(conversation_chunk)
            gpt_result_str = call_gpt_helper(conversation_str)

            # Parse any extra text from the json response
            gpt_result_str = gpt_result_str[gpt_result_str.find("{"): gpt_result_str.rfind("}") + 1]

            gpt_result = json.loads(gpt_result_str)
            write_results(conversation_chunk, gpt_result, output_writer)
            num_chunks_classified += 1
        except Exception as e:
            # Output the failed user_id and context_id to the errors file
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print(conversation_str)
            print('---------------------------------------------------------------')
            print(gpt_result_str)
            print('---------------------------------------------------------------')
            print(f"Error: {e}")
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            errors_writer.writerow([user_id, context_id])
            num_chunks_failed += 1

    return num_chunks_classified, num_chunks_failed

# Classify the messages in the chat messages!
# user_ids: list of the user_ids of users who sent a message
# chat_messages: DataFrame of the chat messages
# output_filename: string of the filename of the output file
# output_fieldnames: list of the fieldnames of the output file
# errors_filename: string of the filename of the errors file
# errors_fieldnames: list of the fieldnames of the errors file
# chunk_size: int of the number of messages to classify at a time
# total_chunks: int of the total number of chunks to classify
def classify_messages(user_ids, chat_messages, output_filename, output_fieldnames, 
                      errors_filename, errors_fieldnames, chunk_size, total_chunks, classified_messages):
    # Initialize the output files
    output_file, output_writer = init_output_file(output_filename, output_fieldnames)
    errors_file, errors_writer = init_output_file(errors_filename, errors_fieldnames)

    count_chunks_classified = 0
    count_chunks_failed = 0
    for user_id in user_ids:
        conversations = get_conversations_for_user(user_id, chat_messages)

        for context_id, chat_conversation in conversations:
            # Classify the messages!
            num_chunks_classified, num_failed = classify_messages_helper(
                user_id, context_id, chat_conversation, output_writer, 
                errors_writer, chunk_size, classified_messages)
            
            # Update the count of chunks classified
            count_chunks_classified += num_chunks_classified
            count_chunks_failed += num_failed

        # Print the progress
        print(f"Progress: {count_chunks_classified}/{total_chunks} chunks classified")

    # Close the output files
    output_file.close()
    errors_file.close()
    print('Total failed chunks:', count_chunks_failed)

# Get the total number of conversation chunks in the dataset
def get_num_conversation_chunks(user_ids, chat_messages, chunk_size, classified_messages):
    count_chunks = 0

    # Loop through each user
    for user_id in user_ids:
        # Get the conversations for this user
        conversations = get_conversations_for_user(user_id, chat_messages)

        # Loop through each conversation and count the number of chunks
        for context_id, chat_conversation in conversations:
            # If the user never sent a message in this conversation, skip
            if never_sent_message(chat_conversation, user_id):
                continue

            # If the messages in this conversation have already been classified, skip
            if was_already_classified(chat_conversation, classified_messages):
                continue

            num_messages = len(chat_conversation)
            num_chunks = num_messages // chunk_size
            if num_messages % chunk_size != 0:
                num_chunks += 1
            count_chunks += num_chunks

    return count_chunks

def classify(output_filename):
    # Load the users who sent messages
    users_sent_messages = get_sent_message()
    user_ids = users_sent_messages['user_id'].unique()

    # Load the chat messages
    chat_messages = get_chat_messages()

    # Define the output file
    output_fieldnames = ['messageId', 'message', 'classification']

    # Define the errors file
    errors_filename = '../parsed_data/message_classification_errors.csv'
    errors_fieldnames = ['user_id', 'context_id']

    # Load the messages that were already classified
    classified_messages = pd.read_csv(output_filename)

    # Get the total number of conversation chunks
    chunk_size = 10
    total_chunks = get_num_conversation_chunks(user_ids, chat_messages, chunk_size, classified_messages)
    print(f"Total number of conversation chunks: {total_chunks}")

    # Classify the messages
    classify_messages(
        user_ids, chat_messages, output_filename, output_fieldnames, errors_filename, 
        errors_fieldnames, chunk_size, total_chunks, classified_messages)

def classify_individual_message(messageId, output_filename, output_fieldnames):
    chat_messages = get_chat_messages()

    try:
        # Get the message
        message = chat_messages[chat_messages['messageId'] == messageId]
        
        # Construct the prompt string
        message_content = message["message"].values[0]
        conversation_str = f'user_message_1: {message_content}\n\n'
        
        # Get GPT's classification
        gpt_result_str = call_gpt_helper(conversation_str)
        gpt_result_str = gpt_result_str[gpt_result_str.find("{"): gpt_result_str.rfind("}") + 1]
        gpt_result = json.loads(gpt_result_str)
        gpt_classification = gpt_result[f"user_message_1"]["classification"]
        print(messageId, message_content, gpt_classification)
        
        # Write the classification to the output file
        output_file, output_writer = init_output_file(output_filename, output_fieldnames)
        output_writer.writerow([messageId, message_content, gpt_classification])
        output_file.close()
    except Exception as e:
        print(f"Error: {e}")

def remove_duplicates(output_filename):
    classified_messages = pd.read_csv(output_filename)
    classified_messages = classified_messages.drop_duplicates(subset=['messageId'])
    classified_messages.to_csv(output_filename, index=False)

def handle_special_case():
    # VukA4tXIhZbRtZZ6ZCr4emZDEf92 is the authorId of the message 8XgRGpaPKzi4IxMB81DO
    # However, the message never appeared in VukA4tXIhZbRtZZ6ZCr4emZDEf92's messages
    # An explanation is that the user changed slides very quickly
    classify_individual_message('8XgRGpaPKzi4IxMB81DO', output_filename, ['messageId', 'message', 'classification'])

def sanity_check(output_filename):
    classified_messages = pd.read_csv(output_filename)
    print(len(classified_messages))

    chat_messages = get_chat_messages()
    experiment_roster = get_experiment_roster()
    unique_user_messages = chat_messages[(chat_messages['authorId'].isin(experiment_roster['user_id'])) & # If I exclude this line, I get 1 more message from the special case^
                                         (chat_messages['user_id'] == chat_messages['authorId'])]['messageId'].unique()
    print(len(unique_user_messages))

    for messageId in unique_user_messages:
        if messageId not in classified_messages['messageId'].values:
            print(messageId)

if __name__ == "__main__":
    output_filename = '../parsed_data/message_classifications_tmp.csv'
    # classify(output_filename)
    # remove_duplicates(output_filename)
    sanity_check(output_filename)
    # handle_special_case()


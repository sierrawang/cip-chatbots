# Chatbot experiment messages are stored at /chatHistory/{userId}/lessons/{lessonId}/messages or /chatHistory/{userId}/assns/{assnId}/messages
# Download a csv of all messages
# The columns are userId, timestamp, lessonId, assnId, message

import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from get_experiment_roster import get_experiment_roster
from timestamps import EXPERIMENT_DEPLOYED_TIMESTAMP, END_OF_EXPERIMENT_TIMESTAMP

import sys
sys.path.insert(1, '../utils')
import util

output_folder = '../downloaded_data/chatMessages_data/'

fieldnames = ['messageId', 'user_id', 'authorId', 'timestamp', 'lessonId', 'assnId', 'message', 'rating']

# Delete and recreate the chatMessages folder
def reset_chatMessages_folder():
    # print("Resetting chatMessages folder")
    if os.path.exists(output_folder):
        os.system(f'rm -rf {output_folder}')
    os.mkdir(output_folder)

def process_user(userId, db):
    user_doc = db.collection('chatHistory').document(userId)

    with open(output_folder + f'{userId}.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate through the lessons subcollection
        lessons_collection = user_doc.collection('lessons')
        for lesson_doc in lessons_collection.list_documents():
            lesson_messages = lesson_doc.collection('messages').list_documents()
            for message_doc in lesson_messages:
                message_data = message_doc.get().to_dict()

                ratings = message_data.get('ratings', {})
                rating = ratings.get(userId, 0)

                # Prepare the row to be written into the CSV
                row = {
                    'messageId': message_doc.id,
                    'user_id': userId,
                    'authorId': message_data['authorId'],
                    'timestamp': message_data['timestamp'],
                    'lessonId': lesson_doc.id,
                    'assnId': '',
                    'message': message_data['content'],
                    'rating': rating
                }
                writer.writerow(row)

        # Iterate through the assns subcollection
        assns_collection = user_doc.collection('assns')
        for assn_doc in assns_collection.list_documents():
            assn_messages = assn_doc.collection('messages').list_documents()
            for message_doc in assn_messages:
                message_data = message_doc.get().to_dict()

                ratings = message_data.get('ratings', {})
                rating = ratings.get(userId, 0)

                # Prepare the row to be written into the CSV
                row = {
                    'messageId': message_doc.id,
                    'user_id': user_doc.id,
                    'authorId': message_data['authorId'],
                    'timestamp': message_data['timestamp'],
                    'lessonId': '',
                    'assnId': assn_doc.id,
                    'message': message_data['content'],
                    'rating': rating
                }
                writer.writerow(row)

def download_messages():
    # print("Downloading chatMessages")

    # Get a reference to the chatHistory collection to stream the data from
    db = util.setup_db()
    
    # Setup database and file writer
    studentUserIds = get_experiment_roster()

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks
        future_to_user = {executor.submit(process_user, userId, db): userId for userId in studentUserIds}
    
        # Wait for tasks to complete
        for future in as_completed(future_to_user):
            userId = future_to_user[future]
            try:
                future.result()
            except Exception as e:
                print(f"download_chat_messages: error processing user {userId}: {e}")

def concat_messages():
    # print("Concatenating chatMessages")
    filename = '../downloaded_data/chat_messages.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for userId in os.listdir(output_folder):
            with open(output_folder + userId, 'r') as user_file:
                reader = csv.DictReader(user_file)
                for row in reader:
                    writer.writerow(row)

def remove_messages_outside_experiment():
    # print("Removing messages outside experiment")
    chat_messages = pd.read_csv('../downloaded_data/chat_messages.csv')
    chat_messages.loc[:, "timestamp"] = pd.to_datetime(chat_messages["timestamp"], format='mixed')
    chat_messages = chat_messages[(chat_messages["timestamp"] > EXPERIMENT_DEPLOYED_TIMESTAMP) & 
                                  (chat_messages["timestamp"] < END_OF_EXPERIMENT_TIMESTAMP)]
    chat_messages.to_csv('../downloaded_data/chat_messages.csv', index=False)

# Remember to call the download_messages function
if __name__ == "__main__":
    reset_chatMessages_folder()
    download_messages()
    concat_messages()
    remove_messages_outside_experiment()
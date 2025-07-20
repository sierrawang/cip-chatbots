import pandas as pd
import os

from download_scripts.get_experiment_roster import load_experiment_roster

# Return a dataframe of all chat messages
def get_chat_messages():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, '../../downloaded_data/chat_messages.csv')
    return pd.read_csv(file_path)

# Return a dataframe of all of the students who sent a message
def get_sent_message():
    chat_messages = get_chat_messages()
    authors = chat_messages['authorId'].unique()
    experiment_roster = load_experiment_roster()
    return experiment_roster[experiment_roster['user_id'].isin(authors)]

# Return the messages sent by the given user
def get_messages_sent_for_user(user_id, chat_messages):
    user_messages = chat_messages[(chat_messages['user_id'] == user_id) &
                                  (chat_messages['authorId'] == user_id)]
    return user_messages

# Return the number of messages sent by the given user
def get_num_messages_sent_for_user(user_id, chat_messages):
    user_messages = get_messages_sent_for_user(user_id, chat_messages)
    return len(user_messages)

# Return whether the user sent a message (1 if they did, 0 otherwise)
def get_user_sent_message(user_id, chat_messages):
    num_sent = get_num_messages_sent_for_user(user_id, chat_messages)
    if num_sent > 0:
        return 1
    else:
        return 0

# Return a list of whether each student sent a message
def get_message_sent_results(df, chat_messages):
    user_ids = df['user_id'].unique()
    results = []
    for user_id in user_ids:
        # Check if the user sent a message
        num_messages = get_num_messages_sent_for_user(user_id, chat_messages)
        if num_messages > 0:
            results.append(1)
        else:
            results.append(0)
    return results

# Return a list of the number of messages sent by each student
# include_all is a boolean that determines whether to include students who never sent a message
def get_num_messages_sent_results(df, chat_messages, include_all=True):
    user_ids = df['user_id'].unique()
    results = []
    for user_id in user_ids:
        # Get the number of messages sent by the user
        num_messages = get_num_messages_sent_for_user(user_id, chat_messages)
        if include_all or (num_messages > 0):
            results.append(num_messages)
    return results
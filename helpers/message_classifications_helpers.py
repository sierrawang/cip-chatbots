import pandas as pd

from chat_usage_helpers import get_messages_sent_for_user

message_classifications = [ 'HOMEWORK', 'CONCEPTUAL', 'AI', 'GREETING', 'GRATITUDE', 'OTHER' ]

def get_message_classifications():
    return pd.read_csv('../parsed_data/message_classifications.csv')

def get_number_messages_sent_are_classification(user_id, classification, classified_messages, chat_messages):
    user_messages = get_messages_sent_for_user(user_id, chat_messages)
    
    # If the user never asked a question, don't include them in the analysis
    if len(user_messages) == 0:
        return -1
    
    # Count all of the messages with the given classification
    specific_messages = 0
    for _,row in user_messages.iterrows():
        message_id = row['messageId']
        message_classification = classified_messages[classified_messages['messageId'] == message_id]['classification'].values[0]
        if message_classification == classification:
            specific_messages += 1

    return specific_messages 

# Return the percent of messages sent by the given user that are the given classification
def get_percent_messages_sent_are_classification(user_id, classification, classified_messages, chat_messages):
    user_messages = get_messages_sent_for_user(user_id, chat_messages)
    
    # If the user never asked a question, don't include them in the analysis
    if len(user_messages) == 0:
        return -1
    
    # Count all of the messages with the given classification
    specific_messages = 0
    total_messages = len(user_messages)
    for index,row in user_messages.iterrows():
        message_id = row['messageId']
        message_classification = classified_messages[classified_messages['messageId'] == message_id]['classification'].values[0]
        if message_classification == classification:
            specific_messages += 1
    return specific_messages / total_messages
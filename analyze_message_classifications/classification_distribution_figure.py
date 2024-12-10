import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import sys
sys.path.insert(1, '../helpers')
from chat_usage_helpers import get_chat_messages
from rosters_helpers import get_basic_personified_students, get_basic_nonpersonified_students, get_ide_personified_students, get_ide_nonpersonified_students
from message_classifications_helpers import message_classifications, get_message_classifications

plt.rcParams['font.family'] = 'Times New Roman'
# plt.rcParams['font.size'] = 20

def init_classification_distribution():
    results = {}
    for classification in message_classifications:
        results[classification] = 0
    return results

# Return the messages that this user sent
def get_user_messages(user_id, chat_messages):
    return chat_messages[(chat_messages['user_id'] == user_id) & (chat_messages['authorId'] == user_id)]

# Return a dictionary where the keys are the classifications and the values are the number of messages
# of that classification that users in the roster sent
def get_distribution_for_roster(df, chat_messages, classified_messages):
    classification_distribution = init_classification_distribution()
    for index,row in df.iterrows():
        user_id = row['user_id']
        user_messages = get_user_messages(user_id, chat_messages)

        for index,row in user_messages.iterrows():
            messageId = row['messageId']
            classification = classified_messages[classified_messages['messageId'] == messageId]['classification'].values[0]
            classification_distribution[classification] += 1
    
    # Convert the counts to percentages
    total_messages = sum(classification_distribution.values())
    for classification, count in classification_distribution.items():
        if total_messages > 0:
            classification_distribution[classification] = count / total_messages * 100
        else:
            classification_distribution[classification] = 0

    return classification_distribution

# Create a bar graph where:
# x-axis: chat type (categories)
# y-axis: the percent of the messages in that chat type
# Each bar should contain the percentage of messages that are 
# classified as each classification for that chat type
def graph_chattype_vs_classification(dfs):
    classified_messages = get_message_classifications()
    chat_messages = get_chat_messages()

    # Get the message distribution for each chat type
    distributions_by_chat_type = {}
    for chat_type, df in dfs.items():
        classification_distribution = get_distribution_for_roster(df, chat_messages, classified_messages)
        distributions_by_chat_type[chat_type] = classification_distribution

    # Initialize the plot
    fig, ax = plt.subplots()
    bar_width = 0.4
    opacity = 0.5
    index = range(len(dfs))
    
    # Initialize position for the group bars
    bar_positions = list(index)
    
    # For storing color for each classification
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']

    # Initialize the bottom of the bars
    bottom_accumulate = [0] * len(dfs)

    # Loop through every message classification
    for i, classification in enumerate(message_classifications):

        # Initialize the percentages for each chat type
        classification_percents = []

        # Get the percentage of messages that are classified as this classification for all chat types
        for chat_type, df in dfs.items():
            # Get the percentage of messages that are classified as this classification
            # for this chat type
            percentage = distributions_by_chat_type[chat_type][classification]
            classification_percents.append(percentage)
        
        # Add this classification to the bar graph
        bars = plt.bar(bar_positions, 
                classification_percents, 
                bar_width, 
                alpha=opacity, 
                color=colors[i], 
                label=classification, 
                bottom=bottom_accumulate)
        
        print(f'{classification}: {classification_percents}')

        # Add labels to the bars
        for i, (bar, label) in enumerate(zip(bars, classification_percents)):
            height = bottom_accumulate[i] + bar.get_height() / 2
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{label:.3f}%', ha='center', va='bottom')
        
        # Update the bottom of the bars
        bottom_accumulate += np.array(classification_percents)

    # plt.xlabel('Chat Type')
    plt.ylabel('% of Messages')
    # plt.title('Distribution of Message Classifications by Chat Type')
    plt.xticks(index, dfs.keys())

    # Add a legend on the outside upper right corner, outside of the plot
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    # plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # dfs = {
    #     'IDE/Agent': get_ide_personified_students(),
    #     'IDE/Tool': get_ide_nonpersonified_students(),
    #     'Basic/Agent': get_basic_personified_students(),
    #     'Basic/Tool': get_basic_nonpersonified_students(),
    # }

    dfs = {
        'IDE': pd.concat([get_ide_personified_students(), get_ide_nonpersonified_students()]),
        'Lessons': pd.concat([get_basic_personified_students(), get_basic_nonpersonified_students()]),
    }

    graph_chattype_vs_classification(dfs)

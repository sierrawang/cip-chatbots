import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from data_analysis.helpers.chat_usage_helpers import get_chat_messages
from data_analysis.helpers.rosters_helpers import get_basic_personified_students, get_basic_nonpersonified_students, get_ide_personified_students, get_ide_nonpersonified_students
from data_analysis.helpers.message_classifications_helpers import message_classifications, get_message_classifications
from data_analysis.helpers.significance_helpers import bootstrap

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
    bar_width = 0.75
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
        # for i, (bar, label) in enumerate(zip(bars, classification_percents)):
        #     height = bottom_accumulate[i] + bar.get_height() / 2
        #     ax.text(bar.get_x() + bar.get_width() / 2, height, f'{label:.3f}%', ha='center', va='bottom')
        
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


# Return a dictionary where the keys are the classifications and the values are the number of messages
# of that classification that users in the roster sent
def get_verbose_distribution_for_roster(df, chat_messages, classified_messages):
    classification_distribution = init_classification_distribution()
    for index,row in df.iterrows():
        user_id = row['user_id']
        user_messages = get_user_messages(user_id, chat_messages)

        for index,row in user_messages.iterrows():
            messageId = row['messageId']
            classification = classified_messages[classified_messages['messageId'] == messageId]['classification'].values[0]
            classification_distribution[classification] += 1

    return classification_distribution

# Return a list wiith a 1 for every message of the given classification and a 0 for every other message
def get_binary_classification_list(classification_distribution, classification):
    binary_list = []
    for classification_name in message_classifications:
        if classification_name == classification:
            # Add a 1 for every message of the given classification
            binary_list += [1] * classification_distribution[classification_name]
        else:
            # Add a 0 for every other message
            binary_list += [0] * classification_distribution[classification_name]
    return binary_list

# Create a bar graph where:
# x-axis: chat type (categories)
# y-axis: the percent of the messages in that chat type
# Each bar should contain the percentage of messages that are 
# classified as each classification for that chat type
def get_statistical_significance(df1, df2):
    classified_messages = get_message_classifications()
    chat_messages = get_chat_messages()

    # Get the message distribution for each df (chat type)
    classification_distribution1 = get_verbose_distribution_for_roster(df1, chat_messages, classified_messages)
    classification_distribution2 = get_verbose_distribution_for_roster(df2, chat_messages, classified_messages)

    for classification in message_classifications:
        binary_results1 = get_binary_classification_list(classification_distribution1, classification)
        binary_results2 = get_binary_classification_list(classification_distribution2, classification)
        results1_mean, results2_mean, pvalue = bootstrap(binary_results1, binary_results2)
        print(f'{classification}: {results1_mean:.3f} vs {results2_mean:.3f} (p-value: {pvalue:.3f})')

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
    get_statistical_significance(dfs['IDE'], dfs['Lessons'])

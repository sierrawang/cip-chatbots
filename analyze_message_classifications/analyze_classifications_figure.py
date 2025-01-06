import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import sys

sys.path.insert(1, '../helpers')
from chat_usage_helpers import get_chat_messages
from rosters_helpers import get_basic_personified_students, get_basic_nonpersonified_students, get_ide_personified_students, get_ide_nonpersonified_students, get_community_personified_students, get_community_nonpersonified_students, get_grounded_personified_students, get_grounded_nonpersonified_students
from course_completion_helpers import get_student_assignment_completion, get_student_lesson_completion
from message_classifications_helpers import get_message_classifications, get_percent_messages_sent_are_classification
from chat_usage_helpers import get_num_messages_sent_for_user

# Return two rosters:
# - one containing the students who sent at least one message of the given message_type
# - and one containing the students who did not send any messages of the given message_type
def split_by_sent_message(roster, message_type, chat_messages, classified_messages):
    # Initialize the two rosters
    asked_one_message_type = []
    did_not_ask_one_message_type = []

    # Loop through every user in the dataframe and determine whether 
    # they sent at least one message of this classification
    for user_id in roster:
        percent_classification = get_percent_messages_sent_are_classification(user_id, message_type, classified_messages, chat_messages)

        # If the user sent at least one message of the given type, 
        # add them to the first roster
        if percent_classification > 0:
            asked_one_message_type.append(user_id)

        elif percent_classification == 0:
            # This excludes users who sent no messages at all
            did_not_ask_one_message_type.append(user_id)

    return {
        'Asked at least one ' + message_type: asked_one_message_type,
        'No ' + message_type: did_not_ask_one_message_type
    }

# Return rosters for each percentile of the number of messages sent
def split_by_number_messages_sent(roster, chat_messages):
    # Compute the number of messages sent for each user
    num_messages_sent_df = []
    for user_id in roster:
        num_user_messages = get_num_messages_sent_for_user(user_id, chat_messages)

        # Only include users who sent a message
        if num_user_messages > 0:
            num_messages_sent_df.append({
                'user_id': user_id,
                'num_messages_sent': num_user_messages
            })

    num_messages_sent_df = pd.DataFrame(num_messages_sent_df)

    # Determine the percentile cutoffs
    percentiles = [0, 25, 50, 75, 100]
    cutoff_values = np.percentile(num_messages_sent_df['num_messages_sent'], percentiles)
    
    # Split the roster into the different percentiles
    groups = {}
    for i in range(len(percentiles) - 1):
        # Determine the bounds for the current percentile
        lower_bound = cutoff_values[i]
        upper_bound = cutoff_values[i + 1]
        label = ""
        
        # Grab the users in the current percentile
        if i == len(percentiles) - 2:
            # Include the upper bound for the last bucket
            group = num_messages_sent_df[(num_messages_sent_df['num_messages_sent'] >= lower_bound) & 
                                         (num_messages_sent_df['num_messages_sent'] <= upper_bound)]
            label = f"{percentiles[i]} - {percentiles[i + 1]} [{lower_bound} - {upper_bound}]"
        else:
            group = num_messages_sent_df[(num_messages_sent_df['num_messages_sent'] >= lower_bound) & 
                                         (num_messages_sent_df['num_messages_sent'] < upper_bound)]
            label = f"{percentiles[i]} - {percentiles[i + 1]} [{lower_bound} - {upper_bound})"
        
        groups[label] = group['user_id'].tolist()

    return groups


def graph_splits_within_splits(df, message_type, engagement_function, metric_name):
    # Load the necessary data
    chat_messages = get_chat_messages()
    classified_messages = get_message_classifications()

    # Split the roster by the number of messages that each user sent
    whole_roster = df['user_id'].tolist()
    splits_by_num_sent = split_by_number_messages_sent(whole_roster, chat_messages)

    # Initialize the results
    averages = {
        f'Asked at least one {message_type}': [],
        f'No {message_type}': []
    }

    sems = {
        f'Asked at least one {message_type}': [],
        f'No {message_type}': []
    }

    colors = {
        f'Asked at least one CONCEPTUAL': '#5c5cf7',
        f'No CONCEPTUAL': '#aaaafa',
        f'Asked at least one HOMEWORK': '#fa52a6',
        f'No HOMEWORK': '#FFB6C1',
    }

    # For each split, split the roster by whether the user sent a message of the given type
    labels = []
    for label, roster in splits_by_num_sent.items():
        labels.append(label)

        # Split the roster by whether the user sent a message of the given type
        splits_by_sent_one = split_by_sent_message(roster, message_type, chat_messages, classified_messages)

        # For the two groups (who either sent at least one message of the given type or did not)
        # compute the engagement results
        for split_name, split_roster in splits_by_sent_one.items():
            print(f'{label} {split_name} {len(split_roster)}')
            
            # Compute the engagement results for each user in the split
            engagement_results = []
            for user_id in split_roster:
                user_result = engagement_function(user_id)
                if user_result >= 0:
                    engagement_results.append(user_result)
            
            # Compute the average and standard error of the mean for the engagement results
            averages[split_name].append(np.mean(engagement_results))
            sems[split_name].append(np.std(engagement_results) / np.sqrt(len(engagement_results)))

    # Plot a line for each split
    plt.figure(figsize=(3, 3))
    for split_name, avg in averages.items():
        plt.errorbar(labels, avg, yerr=sems[split_name], label=split_name, color=colors[split_name], capsize=5, linestyle='-', marker='o')

    plt.xlabel('Number of messages sent (percentiles)')
    plt.ylabel(metric_name)
    plt.ylim(0, 1)
    plt.title(f'{metric_name} by Number of Messages Sent and Whether the User Asked a {message_type} Question')
    # plt.legend()
    plt.show()

def get_all_basic_groups():
    basic_personified_students = get_basic_personified_students()
    basic_nonpersonified_students = get_basic_nonpersonified_students()
    ide_personified_students = get_ide_personified_students()
    ide_nonpersonified_students = get_ide_nonpersonified_students()

    all_basic_groups = pd.concat([basic_personified_students, basic_nonpersonified_students, ide_personified_students, ide_nonpersonified_students])
    return all_basic_groups

def get_all_groups_except_buttons():
    basic_personified_students = get_basic_personified_students()
    basic_nonpersonified_students = get_basic_nonpersonified_students()
    ide_personified_students = get_ide_personified_students()
    ide_nonpersonified_students = get_ide_nonpersonified_students()
    community_personified_students = get_community_personified_students()
    community_nonpersonified_students = get_community_nonpersonified_students()
    grounded_personified_students = get_grounded_personified_students()
    grounded_nonpersonified_students = get_grounded_nonpersonified_students()

    all_groups = pd.concat([basic_personified_students, basic_nonpersonified_students, 
                            ide_personified_students, ide_nonpersonified_students, 
                            community_personified_students, community_nonpersonified_students, 
                            grounded_personified_students, grounded_nonpersonified_students])
    return all_groups

def get_ide_groups():
    ide_personified_students = get_ide_personified_students()
    ide_nonpersonified_students = get_ide_nonpersonified_students()

    ide_groups = pd.concat([ide_personified_students, ide_nonpersonified_students])
    return ide_groups

if __name__ == '__main__':
    df = get_all_basic_groups()

    engagement_functions = {
        'Lesson Completion': get_student_lesson_completion,
        'Assn Completion': get_student_assignment_completion
    }

    message_types = ['CONCEPTUAL', 'HOMEWORK']
    
    for metric_name,engagement_function in engagement_functions.items():
        for message_type in message_types:
            graph_splits_within_splits(df, message_type, engagement_function, metric_name)

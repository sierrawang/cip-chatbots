import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import sys
sys.path.insert(1, '../globals')
from course_completion_helpers import get_lesson_completion, get_message_sent_results
from rosters_helper import get_basic_personified_students, get_basic_nonpersonified_students, get_ide_personified_students, get_ide_nonpersonified_students, get_chat_messages, get_no_chat_students

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 20

# Get the percent of students who sent a message for each group
def percent_sent_message_helper(xlabels, dfs):
    percents_sent_message = []
    percents_sent_message_sem = []
    chat_messages = get_chat_messages()
    for group in xlabels:
        df = dfs[group]
        sent_message_results = get_message_sent_results(df, chat_messages)

        # Multiply by 100 to get percentage
        sent_message_results = [result * 100 for result in sent_message_results]

        percents_sent_message.append(np.mean(sent_message_results))
        percents_sent_message_sem.append(np.std(sent_message_results) / np.sqrt(len(sent_message_results)))

    return percents_sent_message, percents_sent_message_sem

# Get the average lesson completion for each group
def lesson_completion_helper(xlabels, dfs):
    percent_lesson_completion = []
    percent_lesson_completion_sem = []
    for group in xlabels:
        df = dfs[group]
        lesson_results = get_lesson_completion(df)

        # Multiply by 100 to get percentage
        lesson_results = [result * 100 for result in lesson_results]

        percent_lesson_completion.append(np.mean(lesson_results))
        percent_lesson_completion_sem.append(np.std(lesson_results) / np.sqrt(len(lesson_results)))

    return percent_lesson_completion, percent_lesson_completion_sem

# Create a graph where
# 1. The left y-axis is percent of students who sent a message
# 2. The right y-axis is the average percent completion per student
# 3. The x axis is each experiment group (Groups 1, 2, 3, 4, and 11)

# For each experiment group, there are two points (with standard error bars):
# 1. The percent of students in that group who sent a message
# 2. The average assignment completion per student in that group
def graph_usage_vs_completion(dfs, colors):
    xlabels = dfs.keys()

    # Initialize the figure and axis
    fig, ax1 = plt.subplots()

    # Calculate the percent that sent a message for each group
    sent_message_xlabels = xlabels # [group for group in xlabels if group != 'Control\n- No Chat']
    percents_sent_message, percents_sent_message_sem = percent_sent_message_helper(sent_message_xlabels, dfs)

    # Calculate the average lesson completion for each group
    percent_lesson_completion, percent_lesson_completion_sem = lesson_completion_helper(xlabels, dfs)

    # Calculate positions for each group
    # ax1.set_xlabel('Experiment Group')
    # ylabel = 'Percent of Students Who Sent a Message'
    # ax1.set_ylabel('Percent of Students Who Sent a Message', color=colors[0])
    ax1.set_ylim(0, 50)
    ax1.errorbar(sent_message_xlabels, percents_sent_message, yerr=percents_sent_message_sem, color=colors[0], marker='o', linestyle='None', capsize=5) # label=ylabel
    ax1.errorbar(sent_message_xlabels, percents_sent_message, color=colors[0], linestyle='--', alpha=0.5)
    
    ax1.set_yticklabels([])
    ax1.yaxis.set_ticks([])

    # Add padding around the x labels
    ax1.xaxis.labelpad = 10

    # Create a second y-axis for the completion stats
    ax2 = ax1.twinx()
    # ylabel = 'Average Percent Lesson Completion'
    # ax2.set_ylabel(ylabel, color=colors[1])
    ax2.set_ylim(55, 70)
    ax2.errorbar(xlabels, percent_lesson_completion, yerr=percent_lesson_completion_sem, color=colors[1], marker='o', linestyle='None', capsize=5) # label=ylabel
    ax2.errorbar(xlabels, percent_lesson_completion, color=colors[1], linestyle='--', alpha=0.5)

    ax2.set_yticklabels([])
    ax2.yaxis.set_ticks([])

    # Handle the legend
    # lines, labels = ax1.get_legend_handles_labels()
    # lines2, labels2 = ax2.get_legend_handles_labels()
    # ax2.legend(lines + lines2, labels + labels2, loc='upper right')

    # Show plot
    plt.show()

def graph_intersection_between_personification_and_placement():
    basic_personified_students = get_basic_personified_students()
    basic_nonpersonified_students = get_basic_nonpersonified_students()
    ide_personified_students = get_ide_personified_students()
    ide_nonpersonified_students = get_ide_nonpersonified_students()
    control_students = get_no_chat_students()

    dfs = {
        'Group 1\n- IDE\n- Agent-like': ide_personified_students,
        'Group 2\n- IDE\n- Tool-like': ide_nonpersonified_students,
        'Group 3\n- Lessons\n- Agent-like': basic_personified_students,
        'Group 4\n- Lessons\n- Tool-like': basic_nonpersonified_students,
        'Control\n- No Chat': control_students
    }

    colors = ['blue', '#f56c42']

    graph_usage_vs_completion(dfs, colors)

if __name__ == '__main__':
    graph_intersection_between_personification_and_placement()

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
import random


import sys
sys.path.append('../helpers')
from hdi_helpers import get_hdi
from chat_usage_helpers import get_chat_messages, get_sent_message, get_num_messages_sent_for_user, get_user_sent_message
from rosters_helpers import get_student_data, get_experiment_groups
from course_completion_helpers import get_student_assignment_completion, get_student_lesson_completion, get_student_section_attendance

# Print out the correlation coefficient between HDI and the engagement metric
def get_correlation_coefficient(group_name, eval_metric, hdis, results):
    r, pvalue = stats.pointbiserialr(hdis, results) # stats.pearsonr(hdis, results)
    r = round(r, 3)
    rounded_pvalue = round(pvalue, 3)
    if rounded_pvalue < 0.05:
        print(f'{group_name} - {eval_metric}: {r}, p-value: {rounded_pvalue} (significant)')
    else:
        print(f'{group_name} - {eval_metric}: {r}, p-value: {rounded_pvalue}')

def get_student_hdi(user_id, student_data):
    country = student_data[student_data['user_id'] == user_id]['country'].values[0]
    hdi = get_hdi(country)
    if hdi < 0:
        return None
    return hdi

def get_student_age(user_id, student_data):
    return student_data[student_data['user_id'] == user_id]['age'].values[0]

def get_student_gender(user_id, student_data):
    gender = student_data[student_data['user_id'] == user_id]['gender'].values[0]
    if gender == 'female':
        return 0
    elif gender == 'male':
        return 1
    else:
        return None

def get_results_for_students(students, student_data, eval_func, demo_func):
    # Get the results for each country
    demos = []
    results = []

    for _,row in students.iterrows():
        user_id = row['user_id']

        # Get the demographic data for this student
        student_demo = demo_func(user_id, student_data)

        # Get the results for this student
        if student_demo is not None:
            student_result = eval_func(user_id)

            # Update the results for this country
            demos.append(student_demo)
            results.append(student_result)
    
    return demos, results

# Analyze the correlation between HDI and a given metric
def analyze_hdi_vs_metric(group_name, students, student_data, eval_func, demo_func, eval_metric):
    # Get the results for each country
    demos, results = get_results_for_students(students, student_data, eval_func, demo_func)
    get_correlation_coefficient(group_name, eval_metric, demos, results)

# Analyze the correlation between HDI and each metric for all groups
def analyze_hdi_vs_metric_for_all_groups(experiment_groups, engagement_functions, demo_functions, student_data):
    
    # Get the students who sent a message
    sent_message_students = get_sent_message()
    
    for demo_metric, demo_func in demo_functions.items():
        print(f'Analyzing {demo_metric}')
        for eval_metric, eval_func in engagement_functions.items():
            for group_name, students in experiment_groups.items():
                # students = students[students['user_id'].isin(sent_message_students['user_id'])]
                analyze_hdi_vs_metric(group_name, students, student_data, eval_func, demo_func, eval_metric)
            print()
        print()

def load_engagement_functions():
    section_attendance = pd.read_csv("../downloaded_data/section_progress.csv")
    weeks=[0, 1, 2, 3, 4, 5]
    chat_messages = get_chat_messages()
    engagement_functions = {
        'Lesson Completion': get_student_lesson_completion,
        'Assn Completion': get_student_assignment_completion,
        'Section Attendance': lambda user_id: get_student_section_attendance(user_id, section_attendance, weeks),
        'Sent Message': lambda user_id: get_user_sent_message(user_id, chat_messages),
        'Num Messages Sent': lambda user_id: get_num_messages_sent_for_user(user_id, chat_messages)
    }
    return engagement_functions

def load_demo_functions():
    demo_functions = {
        # 'HDI': get_student_hdi,
        # 'Age': get_student_age,
        'Gender': get_student_gender
    }
    return demo_functions

def main():
    student_data = get_student_data()
    experiment_groups = get_experiment_groups()
    engagement_functions = load_engagement_functions()
    demo_functions = load_demo_functions()
    analyze_hdi_vs_metric_for_all_groups(experiment_groups, engagement_functions, demo_functions, student_data)

if __name__ == '__main__':
    main()
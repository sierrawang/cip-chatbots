import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from scipy import stats
import math
import os

from download_scripts.get_experiment_roster import load_experiment_roster
from data_analysis.helpers.hdi_helpers import get_hdi
from data_analysis.helpers.chat_usage_helpers import get_chat_messages, get_num_messages_sent_for_user
from data_analysis.helpers.rosters_helpers import get_student_data, get_experiment_groups, get_ide_personified_students, get_ide_nonpersonified_students, get_buttons_personified_students, get_buttons_nonpersonified_students, get_community_personified_students, get_community_nonpersonified_students, get_basic_personified_students, get_basic_nonpersonified_students, get_no_chat_students
from data_analysis.helpers.course_completion_helpers import get_student_assignment_completion, get_student_lesson_completion, get_student_section_attendance
from data_analysis.helpers.significance_helpers import bootstrap, bootstrap_difference_of_differences

def get_relative_filepath(filepath):
    current_dir = os.path.dirname(__file__)
    filepath = os.path.join(current_dir, filepath)
    return filepath

def graph_demo_vs_metric(rosters, demo_metric, demo_fn, outcome_metric, outcome_fn):
    # Initialize the figure and axis
    fig, ax = plt.subplots(figsize=(4, 4))
    
    # A dictionary to store the results for each group
    # The keys are the group names and the values are dictionaries
    # Each inner dictionary has the demo metric as the key and a list of outcome metric values as the value
    overall_results = {}

    colors = ['#5c2edb', '#f00a3c', 'green', 'orange', 'blue', 'red']
    category_map = {"male": 1, "female": 2}

    # Iterate through each roster and plot the average outcome metric by demo metric
    for group_name, user_ids in rosters.items():
        group_results = {}
        for user_id in user_ids:
            # Add the user's data to the group results
            user_demo = demo_fn(user_id)
            if user_demo is None:
                continue

            group_results[user_demo] = group_results.get(user_demo, []) + [outcome_fn(user_id)]

        # Plot the group's data
        x = []
        y = []
        sems = []
        for demo_val, outcome_vals in group_results.items():
            x.append(category_map[demo_val])
            y.append(np.mean(outcome_vals))
            sems.append(stats.sem(outcome_vals))

        color = colors.pop(0)
        ax.errorbar(x, y, yerr=sems, label=group_name, capsize=5, color=color, fmt='none')
        # faint line connecting the points
        ax.plot(x, y, color=color, alpha=0.5)

        overall_results[group_name] = group_results

    # bring the x values closer together
    ax.set_xlim(0.75, 2.25)

    # Set labels and title
    ax.set_xlabel(demo_metric)
    ax.set_ylabel(outcome_metric)
    ax.set_title(f"{outcome_metric} vs. {demo_metric} by Roster")

    # Show legend
    # ax.legend()
    
    # Set the y limit to be between 0 and 1
    ax.set_ylim(0.4, 0.8)

    # Show the plot
    plt.tight_layout()
    plt.show()

def get_student_gender(user_id, student_data):
    gen = student_data[student_data['user_id'] == user_id]['gender'].values[0] 
    if gen not in ['male', 'female']:
        return None
    return gen

def get_student_age(user_id, student_data):
    return int(student_data[student_data['user_id'] == user_id]['age'].values[0])

def get_student_hdi(user_id, student_data):
    country = student_data[student_data['user_id'] == user_id].iloc[0]['country']
    hdi = get_hdi(country)
    if hdi < 0:
        return None
    return hdi

def get_student_hdi_bucket(user_id, student_data):
    hdi = get_student_hdi(user_id, student_data)
    if hdi is None:
        return None
    if hdi < 0.55:
        return 'Low'
    if hdi < 0.7:
        return 'Medium'
    if hdi < 0.8:
        return 'High'
    
    return 'Very High'

def get_gender_results_for_roster(roster, demo_fn, outcome_fn):
    A_men_results = []
    A_women_results = []
    for user_id in roster:
        user_demo = demo_fn(user_id)
        user_result = outcome_fn(user_id)
        if user_demo == 'male':
            A_men_results.append(user_result)
        elif user_demo == 'female':
            A_women_results.append(user_result)

    return A_men_results, A_women_results

def compare_genders_for_metric(roster_A, roster_B, demo_fn, outcome_metric, outcome_fn):
    
    # Get the results for male and for female for each group
    A_men_results, A_women_results =  get_gender_results_for_roster(roster_A, demo_fn, outcome_fn)
    B_men_results, B_women_results =  get_gender_results_for_roster(roster_B, demo_fn, outcome_fn)    
    
    obs_A_diff, obs_B_diff, p_value = bootstrap_difference_of_differences(A_men_results, A_women_results, B_men_results, B_women_results)

    print(f"{outcome_metric} p-value: {p_value:.3f}")
    print(f"Observed difference of differences: {obs_A_diff:.3f} - {obs_B_diff:.3f} = {obs_A_diff - obs_B_diff:.3f}")

def compare_hdi_influence_between_groups(roster1, roster2, get_hdi_fn, get_outcome_fn):
    # 1. Build a combined DataFrame for the two groups
    data_records = []
    
    # Group 1
    for student in roster1:
        hdi = get_hdi_fn(student)
        if hdi is None:
            continue
        data_records.append({
            'HDI': hdi,
            'Outcome': get_outcome_fn(student),
            'Group': 'Group1'
        })
        
    # Group 2
    for student in roster2:
        hdi = get_hdi_fn(student)
        if hdi is None:
            continue
        data_records.append({
            'HDI': hdi,
            'Outcome': get_outcome_fn(student),
            'Group': 'Group2'
        })
    
    df = pd.DataFrame(data_records)
    
    # 2. Fit a linear model with interaction: Outcome ~ HDI * Group
    #    This includes main effects for HDI, Group, and their interaction.
    model = smf.ols(formula='Outcome ~ HDI * Group', data=df).fit()
    
    # 3. Extract and print key coefficients and p-values
    results = model.params
    p_values = model.pvalues

    # print("\nRegression Results:")
    print(f"Intercept: Coef = {results['Intercept']:.4f}, p = {p_values['Intercept']:.4f}")
    print(f"Group[T.Group2]: Coef = {results['Group[T.Group2]']:.4f}, p = {p_values['Group[T.Group2]']:.4f}")
    print(f"HDI: Coef = {results['HDI']:.4f}, p = {p_values['HDI']:.4f}")
    print(f"HDI:Group[T.Group2]: Coef = {results['HDI:Group[T.Group2]']:.4f}, p = {p_values['HDI:Group[T.Group2]']:.4f}")

    # 4. Return the full model summary in case more details are needed
    return ""

if __name__ == '__main__':
    ide_agent = get_ide_personified_students()
    ide_tool = get_ide_nonpersonified_students()
    ide_students = pd.concat([ide_agent, ide_tool])
    
    basic_agent = get_basic_personified_students()
    basic_tool = get_basic_nonpersonified_students()
    basic_students = pd.concat([basic_agent, basic_tool])

    control = get_no_chat_students()

    rosters = {
        'IDE': ide_students['user_id'],
        'Lessons': basic_students['user_id'],
        'Control': control['user_id']
    }

    student_data = get_student_data()

    # Change all non-binary genders to be 'Other'
    student_data['gender'] = student_data['gender'].apply(lambda x: x if x in ['male', 'female'] else 'other')

    # Define the demographic functions
    get_gender_fn = lambda user_id: get_student_gender(user_id, student_data)
    get_hdi_fn = lambda user_id: get_student_hdi(user_id, student_data)
    get_age_fn = lambda user_id: get_student_age(user_id, student_data)

    # Define the outcome metric functions
    section_attendance = pd.read_csv(
        get_relative_filepath("../../downloaded_data/section_progress.csv"))
    weeks = [0, 1, 2, 3, 4, 5]
    get_section_attendance_fn = lambda user_id: get_student_section_attendance(user_id, section_attendance, weeks)
    chat_messages = get_chat_messages()
    get_messages_fn = lambda user_id: get_num_messages_sent_for_user(user_id, chat_messages)

    # LOOK INTO GENDER!!!
    gender_rosters = {
        'IDE': ide_students['user_id'],
        'Lessons': basic_students['user_id'],
        'Control': control['user_id']
    }
    graph_demo_vs_metric(gender_rosters, 'Gender', get_gender_fn, 'Assignment Completion', get_student_assignment_completion)

    # print("IDE vs. Control")
    # compare_genders_for_metric(rosters['Control'], rosters['IDE'], get_gender_fn, 'Assignment Completion', get_student_assignment_completion)
    # compare_genders_for_metric(rosters['Control'], rosters['IDE'], get_gender_fn, 'Lesson Completion', get_student_lesson_completion)
    # compare_genders_for_metric(rosters['Control'], rosters['IDE'], get_gender_fn, 'Section Attendance', get_section_attendance_fn)

    # print()
    # print("Lessons vs. Control")
    # compare_genders_for_metric(rosters['Lessons'], rosters['Control'], get_gender_fn, 'Assignment Completion', get_student_assignment_completion)
    # compare_genders_for_metric(rosters['Lessons'], rosters['Control'], get_gender_fn, 'Lesson Completion', get_student_lesson_completion)
    # compare_genders_for_metric(rosters['Lessons'], rosters['Control'], get_gender_fn, 'Section Attendance', get_section_attendance_fn)

    # print()
    # print("Lessons vs. IDE")
    # compare_genders_for_metric(rosters['Lessons'], rosters['IDE'], get_gender_fn, 'Assignment Completion', get_student_assignment_completion)
    # compare_genders_for_metric(rosters['Lessons'], rosters['IDE'], get_gender_fn, 'Lesson Completion', get_student_lesson_completion)
    # compare_genders_for_metric(rosters['Lessons'], rosters['IDE'], get_gender_fn, 'Section Attendance', get_section_attendance_fn)

    # LOOK INTO HDI!!!

    # print('Assignment Completion')
    # print("IDE vs. Control")
    # print(compare_hdi_influence_between_groups(rosters['IDE'], rosters['Control'], get_hdi_fn, get_student_assignment_completion))
    # print('Lessons vs. Control')
    # print(compare_hdi_influence_between_groups(rosters['Lessons'], rosters['Control'], get_hdi_fn, get_student_assignment_completion))
    # print('IDE vs. Lessons')
    # print(compare_hdi_influence_between_groups(rosters['IDE'], rosters['Lessons'], get_hdi_fn, get_student_assignment_completion))

    # print('Lesson Completion')
    # print("IDE vs. Control")
    # print(compare_hdi_influence_between_groups(rosters['IDE'], rosters['Control'], get_hdi_fn, get_student_lesson_completion))
    # print("Lessons vs. Control")
    # print(compare_hdi_influence_between_groups(rosters['Lessons'], rosters['Control'], get_hdi_fn, get_student_lesson_completion))
    # print("IDE vs. Lessons")
    # print(compare_hdi_influence_between_groups(rosters['IDE'], rosters['Lessons'], get_hdi_fn, get_student_lesson_completion))

    # print('Section Attendance')
    # print("IDE vs. Control")
    # print(compare_hdi_influence_between_groups(rosters['IDE'], rosters['Control'], get_hdi_fn, get_section_attendance_fn))
    # print("Lessons vs. Control")
    # print(compare_hdi_influence_between_groups(rosters['Lessons'], rosters['Control'], get_hdi_fn, get_section_attendance_fn))
    # print("IDE vs. Lessons")
    # print(compare_hdi_influence_between_groups(rosters['IDE'], rosters['Lessons'], get_hdi_fn, get_section_attendance_fn))

    # LOOK INTO AGE!!!
    # print('Assignment Completion')
    # print("\nIDE vs. Control")
    # compare_hdi_influence_between_groups(rosters['IDE'], rosters['Control'], get_age_fn, get_student_assignment_completion)
    # print('\nLessons vs. Control')
    # compare_hdi_influence_between_groups(rosters['Lessons'], rosters['Control'], get_age_fn, get_student_assignment_completion)
    # print('\nIDE vs. Lessons')
    # compare_hdi_influence_between_groups(rosters['IDE'], rosters['Lessons'], get_age_fn, get_student_assignment_completion)

    # print('Lesson Completion')
    # print("\nIDE vs. Control")
    # compare_hdi_influence_between_groups(rosters['IDE'], rosters['Control'], get_age_fn, get_student_lesson_completion)
    # print("\nLessons vs. Control")
    # compare_hdi_influence_between_groups(rosters['Lessons'], rosters['Control'], get_age_fn, get_student_lesson_completion)
    # print("\nIDE vs. Lessons")
    # compare_hdi_influence_between_groups(rosters['IDE'], rosters['Lessons'], get_age_fn, get_student_lesson_completion)

    # print('Section Attendance')
    # print("\nIDE vs. Control")
    # compare_hdi_influence_between_groups(rosters['IDE'], rosters['Control'], get_age_fn, get_section_attendance_fn)
    # print("\nLessons vs. Control")
    # compare_hdi_influence_between_groups(rosters['Lessons'], rosters['Control'], get_age_fn, get_section_attendance_fn)
    # print("\nIDE vs. Lessons")
    # compare_hdi_influence_between_groups(rosters['IDE'], rosters['Lessons'], get_age_fn, get_section_attendance_fn)

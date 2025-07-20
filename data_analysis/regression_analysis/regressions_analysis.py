import numpy as np
import os
import csv
from tabulate import tabulate
import pandas as pd
import statsmodels.formula.api as smf
# import sys
# sys.path.insert(1, '../helpers')
# from rosters_helpers import get_student_data, NO_CHAT, GROUNDED, GROUNDED_PERSONIFIED, BASIC, BASIC_PERSONIFIED, COMMUNITY, COMMUNITY_PERSONIFIED, BUTTONS, BUTTONS_PERSONIFIED, IDE, IDE_PERSONIFIED
# from course_completion_helpers import get_student_assignment_completion, get_student_lesson_completion, get_student_section_attendance
# from forum_usage_helpers import get_num_forum_posts_for_user, get_user_made_post
# from chat_usage_helpers import get_num_messages_sent_for_user, get_chat_messages, get_user_sent_message
# from diagnostic_helpers import get_student_diagnostic_participation, get_student_diagnostic_score

from data_analysis.helpers.rosters_helpers import (
    get_student_data,
    NO_CHAT, GROUNDED, GROUNDED_PERSONIFIED, BASIC, BASIC_PERSONIFIED,
    COMMUNITY, COMMUNITY_PERSONIFIED, BUTTONS, BUTTONS_PERSONIFIED,
    IDE, IDE_PERSONIFIED
)

from data_analysis.helpers.course_completion_helpers import (
    get_student_assignment_completion,
    get_student_lesson_completion,
    get_student_section_attendance
)

from data_analysis.helpers.forum_usage_helpers import (
    get_num_forum_posts_for_user,
    get_user_made_post
)

from data_analysis.helpers.chat_usage_helpers import (
    get_num_messages_sent_for_user,
    get_chat_messages,
    get_user_sent_message
)

from data_analysis.helpers.diagnostic_helpers import (
    get_student_diagnostic_participation,
    get_student_diagnostic_score
)

from download_scripts.get_experiment_roster import load_experiment_roster

# Return the country of the user
def get_in_usa(user_id, student_data):
    country = student_data[student_data['user_id'] == user_id].iloc[0]['country']
    if country == 'United States':
        return 1
    else:
        return 0

# Return the stored age of the user
def get_age(user_id, student_data):
    age = student_data[student_data['user_id'] == user_id].iloc[0]['age']
    if age < 0:
        # Determine the average age of the students
        age = student_data['age'].mean()
    return age  

def get_female(user_id, student_data):
    gender = student_data[student_data['user_id'] == user_id].iloc[0]['gender']
    if gender == 'female':
        return 1
    else:
        return 0
    
def get_ide(chat_type):
    if chat_type == IDE or chat_type == IDE_PERSONIFIED:
        return 1
    else:
        return 0
    
def get_agent(chat_type):
    if (chat_type == GROUNDED_PERSONIFIED or chat_type == BASIC_PERSONIFIED or 
        chat_type == COMMUNITY_PERSONIFIED or chat_type == BUTTONS_PERSONIFIED or 
        chat_type == IDE_PERSONIFIED):
        return 1
    else:
        return 0
    
def get_community(chat_type):
    if chat_type == COMMUNITY or chat_type == COMMUNITY_PERSONIFIED:
        return 1
    else:
        return 0
    
def get_rag(chat_type):
    if chat_type == GROUNDED or chat_type == GROUNDED_PERSONIFIED:
        return 1
    else:
        return 0
    
def get_buttons(chat_type):
    if chat_type == BUTTONS or chat_type == BUTTONS_PERSONIFIED:
        return 1
    else:
        return 0
    
def get_control(chat_type):
    if chat_type == NO_CHAT:
        return 1
    else:
        return 0

def get_relative_filepath(filepath):
    current_dir = os.path.dirname(__file__)
    filepath = os.path.join(current_dir, filepath)
    return filepath

# Output a csv with all of the data needed to perform the mixed methods analysis
def make_csv(output_filename='../../parsed_data/mixed_effects_data.csv'):
    experiment_roster = load_experiment_roster()
    student_data = get_student_data()
    chat_messages = get_chat_messages()

    section_attendance = pd.read_csv(
        get_relative_filepath('../../downloaded_data/section_progress.csv'))

    fieldnames = ['user_id', 
                  'Female', 'Age', 'In_USA', 'IDE', 'Agent', 
                  'RAG', 'Community', 'Buttons', 'Control',
                  'Section_ID', 
                  'Sent_Message', 'Message_Count', 
                  'Made_Post', 'Post_Count',
                  'Assignment_Completion', 'Lesson_Completion', 'Section_Attendance',
                  'Took_Exam', 'Exam_Score']
    
    output_filename = get_relative_filepath(output_filename)
    with open(output_filename, 'w') as csvfile:
        # Write the header
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for _, row in experiment_roster.iterrows():
            user_row = {}
            user_row['user_id'] = row['user_id']

            # Get demographic details
            user_row['Female'] = get_female(row['user_id'], student_data)
            user_row['Age'] = get_age(row['user_id'], student_data)
            user_row['In_USA'] = get_in_usa(row['user_id'], student_data)

            # Get chat type details
            user_row['IDE'] = get_ide(row['chatType'])
            user_row['Agent'] = get_agent(row['chatType'])
            user_row['RAG'] = get_rag(row['chatType'])
            user_row['Community'] = get_community(row['chatType'])
            user_row['Buttons'] = get_buttons(row['chatType'])

            user_row['Control'] = get_control(row['chatType'])

            user_row['Section_ID'] = row['section_id']
            
            # Dependent variables
            user_row['Sent_Message'] = get_user_sent_message(row['user_id'], chat_messages)
            user_row['Message_Count'] = get_num_messages_sent_for_user(row['user_id'], chat_messages)
            user_row['Made_Post'] = get_user_made_post(row['user_id'], 'posts', experiment_roster)
            user_row['Post_Count'] = get_num_forum_posts_for_user(row['user_id'], 'posts', experiment_roster)
            user_row['Took_Exam'] = get_student_diagnostic_participation(row['user_id'])
            user_row['Exam_Score'] = get_student_diagnostic_score(row['user_id'], -1)
            user_row['Lesson_Completion'] = get_student_lesson_completion(row['user_id'])
            user_row['Assignment_Completion'] = get_student_assignment_completion(row['user_id'])
            user_row['Section_Attendance'] = get_student_section_attendance(row['user_id'], section_attendance, [0, 1, 2, 3, 4, 5])

            writer.writerow(user_row)

def perform_regression_analysis(true_data, independent_variables, dv):
    binary_dvs = ['Sent_Message', 'Made_Post', 'Took_Exam']
    # count_dvs = ['Message_Count', 'Post_Count']
    continuous_dvs = ['Assignment_Completion', 'Lesson_Completion', 'Section_Attendance', 'Exam_Score']

    # Perform a regression analysis for each dependent variable and print the results
    # Make a copy of the data
    data = true_data.copy()

    if dv == 'Message_Count':
        # Drop the rows where the message count is <= 0
        # These are the students who did not send a message
        data = data[data[dv] > 0]

        # Remove the control group since this dv is trivially 0 for them
        data = data[data['Control'] == 0]
        ivs = [iv for iv in independent_variables if iv != 'Control'] 

        # Perform a Poisson regression since this is count data
        formula = f"{dv} ~ " + " + ".join(ivs)
        model = smf.poisson(formula=formula, data=data).fit(disp=False)
        print(f"\n=== Poisson Regression for {dv} ===")
        print(model.summary())
        return model

    elif dv == 'Sent_Message':
        # Drop the control group since this dv is trivially 0 for them
        data = data[data['Control'] == 0]
        ivs = [iv for iv in independent_variables if iv != 'Control'] 

        # Perform a logistic regression since this is binary data
        formula = f"{dv} ~ " + " + ".join(ivs)
        model = smf.logit(formula=formula, data=data).fit(disp=False)
        print(f"\n=== Logistic Regression for {dv} ===")
        print(model.summary())
        return model

    elif dv == 'Post_Count':
        # Drop the rows where the post count is <= 0
        # These are the students who did not make a post
        data = data[data[dv] > 0]
        # print(data.head())

        # Perform a Poisson regression since this is count data
        formula = f"{dv} ~ " + " + ".join(independent_variables)
        model = smf.poisson(formula=formula, data=data).fit(disp=False)
        print(f"\n=== Poisson Regression for {dv} ===")
        print(model.summary())
        return model

    else:
        # For all remaining dependent variables, we can use the full dataset
        # and all independent variables

        formula = f"{dv} ~ " + " + ".join(independent_variables)
        
        if dv in binary_dvs:
            # Logistic regression for binary
            model = smf.logit(formula=formula, data=data).fit(disp=False)
            print(f"\n=== Logistic Regression for {dv} ===")
            print(model.summary())
            return model

        elif dv in continuous_dvs:
            # OLS for continuous
            model = smf.ols(formula=formula, data=data).fit()
            print(f"\n=== OLS for {dv} ===")
            print(model.summary())
            return model
        else:
            assert False, 'Unknown dependent variable!'

def output_all_regressions_in_one_table(output_filename='./tables/regressions_all.tex'):
    # Load the data
    # This dataframe has a row for each student, and columns for each of the variables we want to analyze
    true_data = pd.read_csv(get_relative_filepath('../../parsed_data/mixed_effects_data.csv'))

    # Normalize the Age column
    true_data['Age'] = (true_data['Age'] - true_data['Age'].mean()) / true_data['Age'].std()

    # Define the independent variables
    demographic_covariates = ['Female', 'Age', 'In_USA'] 
    primary_predictors = ['Agent', 'IDE', 'Community', 'RAG', 'Buttons', 'Control']
    independent_variables = demographic_covariates + primary_predictors

    # Define the dependent variables
    dependent_variables = ['Sent_Message', 'Message_Count', 
                           'Assignment_Completion', 'Lesson_Completion', 'Section_Attendance',
                           'Made_Post', 'Post_Count', 
                           'Took_Exam', 'Exam_Score']

    # Initialize the table string
    table = """\\begin{table*}[t]
\\begin{center}
\\begin{tabularx}{\\textwidth}{l"""

    # Add a column for each independent variable
    col_names = []
    for iv in independent_variables:
        table += "X"
        col_names.append(iv.replace("_", " "))

    table += "}\n"

    # Add the header row
    table += "\\toprule\n"
    table += "Dependent Variable & " + " & ".join(col_names) + " \\\\\n"
    table += "\\midrule\n"

    # Add a row for each dependent variable
    for dependent_variable in dependent_variables:
        # Get the regression results
        result = perform_regression_analysis(true_data, independent_variables, dependent_variable)

        # Extract the relevant results
        row_name = dependent_variable.replace("_", " ")
        table += f"{row_name}"
        
        for iv in independent_variables:
            coef = result.params.get(iv, float('nan'))
            pval = result.pvalues.get(iv, float('nan'))

            # Format the coefficient and p-value
            direction = '+' if coef > 0 else '-'
            rounded_coef = round(coef, 2)
            abs_rounded_coef = abs(rounded_coef)

            if pval < 0.001:
                table += f" & {direction}{abs_rounded_coef} ***"
            elif pval < 0.01:
                table += f" & {direction}{abs_rounded_coef} **"
            elif pval < 0.05:
                table += f" & {direction}{abs_rounded_coef} *"
            else:
                table += f" & {direction}{abs_rounded_coef}"

        table += f" \\\\\n"

    # Add the bottom rule
    table += "\\bottomrule\n"
    table += "\\end{tabularx}\n"
    table += "\\end{center}\n"
    table += "\\caption{Regression model results for all dependent variables.}\n"
    table += "\\label{tab:regression_results}\n"
    table += "\\end{table*}\n"

    # Save the table to a file
    output_filename = get_relative_filepath(output_filename)
    with open(output_filename, "w") as f:
        f.write(table)
    print(f"Table saved to {output_filename}.")


if __name__ == '__main__':
    # make_csv()
    output_all_regressions_in_one_table()
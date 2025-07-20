import numpy as np
import csv
from tabulate import tabulate
import pandas as pd
import statsmodels.formula.api as smf
import os

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

from data_analysis.helpers.hdi_helpers import get_hdi

from download_scripts.get_experiment_roster import load_experiment_roster


# import sys
# sys.path.insert(1, '../helpers')
# from rosters_helpers import get_student_data, NO_CHAT, GROUNDED, GROUNDED_PERSONIFIED, BASIC, BASIC_PERSONIFIED, COMMUNITY, COMMUNITY_PERSONIFIED, BUTTONS, BUTTONS_PERSONIFIED, IDE, IDE_PERSONIFIED
# from course_completion_helpers import get_student_assignment_completion, get_student_lesson_completion, get_student_section_attendance
# from forum_usage_helpers import get_num_forum_posts_for_user, get_user_made_post
# from chat_usage_helpers import get_num_messages_sent_for_user, get_chat_messages, get_user_sent_message
# from diagnostic_helpers import get_student_diagnostic_participation, get_student_diagnostic_score
# from hdi_helpers import get_hdi

# sys.path.insert(1, '../download_scripts')
# from get_experiment_roster import load_experiment_roster

def get_chatbot_placement(chat_type):
    if chat_type == NO_CHAT:
        return 'Control'
    elif chat_type == IDE or chat_type == IDE_PERSONIFIED:
        return 'IDE'
    else:
        return 'Lessons'

def get_chatbot_personification(chat_type):
    if chat_type == NO_CHAT:
        return 'Control'
    elif (chat_type == GROUNDED_PERSONIFIED or chat_type == BASIC_PERSONIFIED or 
        chat_type == COMMUNITY_PERSONIFIED or chat_type == BUTTONS_PERSONIFIED or 
        chat_type == IDE_PERSONIFIED):
        return 'Agent'
    else:
        return 'Tool'

def get_chatbot_functionality(chat_type):
    if chat_type == NO_CHAT:
        return 'Control'
    elif (chat_type == BASIC or chat_type == BASIC_PERSONIFIED or chat_type == IDE or chat_type == IDE_PERSONIFIED):
        return 'Basic'
    elif (chat_type == GROUNDED or chat_type == GROUNDED_PERSONIFIED):
        return 'Grounded'
    elif (chat_type == COMMUNITY or chat_type == COMMUNITY_PERSONIFIED):
        return 'Community'
    elif (chat_type == BUTTONS or chat_type == BUTTONS_PERSONIFIED):
        return 'Buttons'
    
    assert False, f"Unknown chat type: {chat_type}"

def get_experiment_group(chat_type):
    return f'{get_chatbot_placement(chat_type)}_{get_chatbot_personification(chat_type)}_{get_chatbot_functionality(chat_type)}'

# Return the country of the user
def get_in_usa(user_id, student_data):
    country = student_data[student_data['user_id'] == user_id].iloc[0]['country']
    if country == 'United States':
        return 1
    else:
        return 0

def get_student_hdi(user_id, student_data):
    country = student_data[student_data['user_id'] == user_id].iloc[0]['country']
    hdi = get_hdi(country)
    if hdi < 0:
        return None
    return hdi

# Return the stored age of the user
def get_age(user_id, student_data):
    age = student_data[student_data['user_id'] == user_id].iloc[0]['age']
    if age < 0:
        # Determine the average age of the students
        age = student_data['age'].mean()
    return age  

# Return the gender of the user
def get_gender(user_id, student_data):
    gender = student_data[student_data['user_id'] == user_id].iloc[0]['gender']
    if gender == 'female' or gender == 'male':
        return gender
    else:
        return 'other'

def get_female(user_id, student_data):
    gender = student_data[student_data['user_id'] == user_id].iloc[0]['gender']
    if gender == 'female':
        return 1
    else:
        return 0
    
def get_male(user_id, student_data):
    gender = student_data[student_data['user_id'] == user_id].iloc[0]['gender']
    if gender == 'male':
        return 1
    else:
        return 0

def get_other_gender(user_id, student_data):
    gender = student_data[student_data['user_id'] == user_id].iloc[0]['gender']
    if gender != 'male' and gender != 'female':
        return 1
    else:
        return 0

def get_lessons(chat_type):
    if chat_type == NO_CHAT or chat_type == IDE or chat_type == IDE_PERSONIFIED:
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
    
def get_tool(chat_type):
    if (chat_type == GROUNDED or chat_type == BASIC or 
        chat_type == COMMUNITY or chat_type == BUTTONS or 
        chat_type == IDE):
        return 1
    else:
        return 0
    
def get_basic(chat_type):
    if chat_type == BASIC or chat_type == BASIC_PERSONIFIED:
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

def get_relative_filename(output_filename='../../parsed_data/demo_data.csv'):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, output_filename)
    return file_path

# Output a csv with all of the data needed to perform the mixed methods analysis
def make_csv(output_filename):
    experiment_roster = load_experiment_roster()
    student_data = get_student_data()
    chat_messages = get_chat_messages()
    section_attendance = pd.read_csv(get_relative_filename("../../downloaded_data/section_progress.csv"))

    fieldnames = ['user_id', 
                  'Female', 'Age', 'In_USA', 'HDI', 'IDE', 'Agent', 
                  'RAG', 'Community', 'Buttons', 'Control', 'Chat_Type',
                  'Section_ID', 
                  'Sent_Message', 'Message_Count', 
                  'Made_Post', 'Post_Count',
                  'Assignment_Completion', 'Lesson_Completion', 'Section_Attendance',
                  'Took_Exam', 'Exam_Score']
    
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
            user_row['HDI'] = get_student_hdi(row['user_id'], student_data)
            user_row['Chat_Type'] = row['chatType']

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

def get_chat_type_name(chat_type):
    if chat_type == NO_CHAT:
        return 'Control'
    elif chat_type == IDE:
        return 'IDE (Tool)'
    elif chat_type == GROUNDED:
        return 'RAG (Tool)'
    elif chat_type == BASIC:
        return 'Basic (Tool)'
    elif chat_type == COMMUNITY:
        return 'Community (Tool)'
    elif chat_type == BUTTONS:
        return 'Buttons (Tool)'
    elif chat_type == IDE_PERSONIFIED:
        return 'IDE (Agent)'
    elif chat_type == GROUNDED_PERSONIFIED:
        return 'RAG (Agent)'
    elif chat_type == BASIC_PERSONIFIED:
        return 'Basic (Agent)'
    elif chat_type == COMMUNITY_PERSONIFIED:
        return 'Community (Agent)'
    elif chat_type == BUTTONS_PERSONIFIED:
        return 'Buttons (Agent)'
    else:
        assert False, f"Unknown chat type: {chat_type}"

def output_all_regressions_in_one_table(chat_type):
    # Load the data
    # This dataframe has a row for each student, and columns for each of the variables we want to analyze
    true_data = pd.read_csv(get_relative_filename('../../parsed_data/demo_data.csv'))

    # Normalize the Age column
    true_data['Age'] = (true_data['Age'] - true_data['Age'].mean()) / true_data['Age'].std()

    # Normalize the HDI column
    true_data['HDI'] = (true_data['HDI'] - true_data['HDI'].mean()) / true_data['HDI'].std()

    # Filter to only students with this chat type
    true_data = true_data[true_data['Chat_Type'] == chat_type]
    output_filename=get_relative_filename(f'./tables/all.tex')

    # Define the independent variables
    independent_variables = ['Female', 'Age', 'HDI'] #'In_USA', 

    # Define the dependent variables
    dependent_variables = ['Sent_Message', 'Message_Count', 
                           'Assignment_Completion', 'Lesson_Completion', 'Section_Attendance']
                        #    'Took_Exam', 'Exam_Score', 'Made_Post', 'Post_Count']

    if get_control(chat_type) == 1:
        # If this is the control group, ignore chatbot-related variables
        dependent_variables = dependent_variables[2:]

    # Initialize the table string
    table = """\\begin{table}[t]
\\begin{center}
\\begin{tabularx}{\\columnwidth}{l"""

    # Add a column for each independent variable
    col_names = []
    for iv in independent_variables:
        table += "X"
        col_names.append(iv.replace("_", " "))

    table += "}\n"

    # Add the header row
    table += "\\toprule\n"
    table += "D.V. & " + " & ".join(col_names) + " \\\\\n"
    table += "\\midrule\n"

    # Add a row for each dependent variable
    for dependent_variable in dependent_variables:
        # Get the regression results
        result = perform_regression_analysis(true_data, independent_variables, dependent_variable)

        # Extract the relevant results
        row_name = dependent_variable.replace("_", " ")[:9]
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

    chat_type_name = get_chat_type_name(chat_type)
    table += f"\\caption{{{chat_type_name}}}\n"
    table += "\\label{tab:demo_table}\n"
    table += "\\end{table}\n\n"

    # Save the table to a file
    with open(output_filename, "a") as f:
        f.write(table)
    print(f"Table saved to {output_filename}.")

# Output a latex table that has a row per experiment group
# and a column for each demographic variable (female, age, hdi) and the size of the group
# And the value shows the coefficient for that demographic variable and the p-value
def output_table_for_metric(chat_types, data, output_filename):
    # Initialize the table string
    table = """\\begin{table*}[t]
\\centering
\\begin{tabularx}{\\textwidth}{l"""

    independent_variables = ['Female', 'Age', 'HDI']

    # Add a column for each independent variable
    col_names = ['Group']
    for i in range(3):
        for iv in independent_variables:
            table += "X"
            col_names.append(f"\\multicolumn{{1}}{{c}}{{{iv}}}")
    table += "}\n"

    # Add the header row
    table += "\\toprule\n"
    table += "& \\multicolumn{3}{c}{\\textbf{Assignment Completion}} & \\multicolumn{3}{c}{\\textbf{Lesson Completion}} & \\multicolumn{3}{c}{\\textbf{Section Attendance}} \\\\"
    table += " & ".join(col_names) + " \\\\ \n"
    table += "\\cmidrule(r{3mm}){1-1} \\cmidrule(r{3mm}){2-4} \\cmidrule(r{3mm}){5-7} \\cmidrule(r{3mm}){8-10} \n"

    # Populate the row for each chat type
    for chat_type in chat_types:
        group_name = get_chat_type_name(chat_type)
        group_data = data[data['Chat_Type'] == chat_type]
        # group_size = len(group_data)

        row_string = f"{group_name} "

        for evaluation_metric in ['Assignment_Completion', 'Lesson_Completion', 'Section_Attendance']:
            # Get the regression results
            result = perform_regression_analysis(group_data, independent_variables, evaluation_metric)
            for iv in independent_variables:
                coef = result.params.get(iv, float('nan'))
                pval = result.pvalues.get(iv, float('nan'))

                # Format the coefficient and p-value
                direction = '+' if coef > 0 else '-'
                rounded_coef = round(coef, 2)
                abs_rounded_coef = abs(rounded_coef)

                if pval < 0.001:
                    row_string += f" & {direction}{abs_rounded_coef} ***"
                elif pval < 0.01:
                    row_string += f" & {direction}{abs_rounded_coef} **"
                elif pval < 0.05:
                    row_string += f" & {direction}{abs_rounded_coef} *"
                else:
                    row_string += f" & {direction}{abs_rounded_coef}"

        table += f"{row_string}\\\\\n"

    # Add the bottom rule
    table += "\\bottomrule\n"
    table += "\\end{tabularx}\n"

    caption = evaluation_metric.replace("_", " ")
    table += f"\\caption{{{caption}}}\n"
    table += "\\label{tab:demo_table}\n"
    table += "\\end{table*}\n\n"

    # Save the table to a file
    with open(output_filename, "w") as f:
        f.write(table)
    print(f"Table saved to {output_filename}.")


if __name__ == '__main__':
    # make_csv()
    evaluation_metrics = ['Assignment_Completion', 'Lesson_Completion', 'Section_Attendance']
    chat_types = [NO_CHAT, 
                  IDE, IDE_PERSONIFIED, 
                  BASIC, BASIC_PERSONIFIED, 
                  GROUNDED, GROUNDED_PERSONIFIED, 
                  COMMUNITY, COMMUNITY_PERSONIFIED, 
                  BUTTONS,  BUTTONS_PERSONIFIED]
    data = pd.read_csv(get_relative_filename('../../parsed_data/demo_data.csv'))

    # Normalize the Age and HDI columns
    data['Age'] = (data['Age'] - data['Age'].mean()) / data['Age'].std()
    data['HDI'] = (data['HDI'] - data['HDI'].mean()) / data['HDI'].std()

    # for evaluation_metric in evaluation_metrics:
    # output_filename=f'./tables/{evaluation_metric}.tex'
    output_table_for_metric(chat_types, data, 
                            get_relative_filename('./tables/evaluation_metrics.tex'))
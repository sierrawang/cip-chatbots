import numpy as np
import csv
from tabulate import tabulate
import pandas as pd
import statsmodels.formula.api as smf
import sys
sys.path.insert(1, '../helpers')
from rosters_helpers import get_student_data, NO_CHAT, GROUNDED, GROUNDED_PERSONIFIED, BASIC, BASIC_PERSONIFIED, COMMUNITY, COMMUNITY_PERSONIFIED, BUTTONS, BUTTONS_PERSONIFIED, IDE, IDE_PERSONIFIED
from course_completion_helpers import get_student_assignment_completion, get_student_lesson_completion, get_student_section_attendance
from forum_usage_helpers import get_num_forum_posts_for_user, get_user_made_post
from chat_usage_helpers import get_num_messages_sent_for_user, get_chat_messages, get_user_sent_message
from diagnostic_helpers import get_student_diagnostic_participation, get_student_diagnostic_score

sys.path.insert(1, '../download_scripts')
from get_experiment_roster import load_experiment_roster

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

# Output a csv with all of the data needed to perform the mixed methods analysis
def make_csv(output_filename='../parsed_data/mixed_effects_data.csv'):
    experiment_roster = load_experiment_roster()
    student_data = get_student_data()
    chat_messages = get_chat_messages()
    section_attendance = pd.read_csv("../downloaded_data/section_progress.csv")

    fieldnames = ['user_id', 
                  'Female', 'Age', 'In_USA', 'IDE', 'Agent', 
                  'RAG', 'Community', 'Buttons', 'Control',
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

def get_mixed_effects_results(fixed_effects, dependent_variable, random_effect, mixed_effects_data):
    # Duplicate the data
    data = mixed_effects_data

    # Check if we need to drop users who did not participate
    # NOTE - for some reason, removing students who did not send a message
    # causes a singularity in the matrix... Maybe investigate this in the future, 
    # but for now, I think it's fine to just include these students in the model.
    if dependent_variable == 'Message_Count' or dependent_variable == 'Post_Count':
        # Drop rows where dependent_variable <= 0 
        # These are the students who did not send a message/make a post
        data = data[data[dependent_variable] > 0]

        # Output the dataframe to a file for debugging
        data.to_csv(f'./{dependent_variable}_data.csv', index=False)
    
    if dependent_variable == 'Exam_Score':
        # Drop negative values 
        # These are the students who didn't take the exam
        data = data[data[dependent_variable] >= 0]
    
    # Check if we need to drop the control group
    if dependent_variable == 'Sent_Message' or dependent_variable == 'Message_Count':
        data = data[data['Control'] == 0]

        # Remove the control group from the fixed effects
        fixed_effects = [fe for fe in fixed_effects if fe != 'Control']

    # Construct the formula: dependent_variable ~ fixed_effects
    formula = f"{dependent_variable} ~ {' + '.join(fixed_effects)}"

    # Fit the mixed model
    model = smf.mixedlm(formula, data=data, groups=data[random_effect])
    result = model.fit()

    return result

# Output a latex table where there is a row for each dependent variable and a column for each fixed effect. 
# The value in each cell is the coefficient and p-value in parentheses.
# There is a model for each dependent variable, and the fixed effects are the same for each model.
# There should also be a converged column that indicates whether the model converged for that dependent variable.
def output_all_mixed_methods_in_one_table(mixed_effects_data, fixed_effects, random_effect, dependent_variables, output_filename='./tables/mixed_methods_all.tex'):
    # Initialize the table string
    table = """\\begin{table*}[t]
\\begin{center}
\\begin{tabularx}{\\textwidth}{l"""

    # Fit a model to determine all fixed effect names, including categorical levels
    test_formula = f"{dependent_variables[0]} ~ {' + '.join(fixed_effects)}"
    test_model = smf.mixedlm(test_formula, data=mixed_effects_data, groups=mixed_effects_data[random_effect])
    test_result = test_model.fit()
    all_fixed_effects = test_result.model.exog_names

    # Add a column for each fixed effect
    col_names = []
    for fe in all_fixed_effects:
        if fe == 'Intercept':
            continue

        table += "X"
        col_names.append(fe.replace("_", " "))
    table += "X}\n"  # Add a column for the converged column

    # Add the header row
    table += "\\toprule\n"
    table += "Dependent Variable & Converged & " + " & ".join(col_names) + " \\\\\n"
    table += "\\midrule\n"

    # Add a row for each dependent variable
    for dependent_variable in dependent_variables:
        # Get the mixed effects result
        result = get_mixed_effects_results(fixed_effects, dependent_variable, random_effect, mixed_effects_data)

        # Extract the relevant results
        converged = result.converged
        row_name = dependent_variable.replace("_", " ")
        table += f"{row_name} & {'Yes' if converged else 'No'} "
        
        for fixed_effect in all_fixed_effects:
            if fixed_effect == 'Intercept':
                continue

            coef = result.fe_params.get(fixed_effect, float('nan'))
            pval = result.pvalues.get(fixed_effect, float('nan'))
            if pval < 0.001:
                table += f" & {coef:.3f}***"
            elif pval < 0.01:
                table += f" & {coef:.3f}**"
            elif pval < 0.05:
                table += f" & {coef:.3f}*"
            else:
                table += f" & {coef:.3f}"
        table += f" \\\\\n"

    # Add the bottom rule
    table += "\\bottomrule\n"
    table += "\\end{tabularx}\n"
    table += "\\end{center}\n"
    table += "\\caption{Mixed-effects model results for all dependent variables.}\n"
    table += "\\label{tab:mixed_methods}\n"
    table += "\\end{table*}\n"

    # Save the table to a file
    with open(output_filename, "w") as f:
        f.write(table)
    print(f"Table saved to {output_filename}.")

def output_mixed_effects_table():
    # Define all of the fixed effects that we are analyzing
    # These are either demographic characteristics, or chatbot features based 
    # on the student's experiment group
    demographic_covariates = ['Female', 'Age', 'In_USA'] 
    primary_predictors = ['Agent', 'IDE', 'Community', 'RAG', 'Buttons', 'Control']
    fixed_effects = demographic_covariates + primary_predictors

    # The random effect is the student's section
    random_effect = 'Section_ID'
    
    mixed_effects_data = pd.read_csv('../parsed_data/mixed_effects_data.csv')

    # Create a model for each dependent variable that we analyze in the paper
    dependent_variables = ['Sent_Message', 'Message_Count', 
                           'Assignment_Completion', 'Lesson_Completion', 'Section_Attendance',
                           'Made_Post', 'Post_Count', 
                           'Took_Exam', 'Exam_Score']

    # Output the results!
    output_all_mixed_methods_in_one_table(mixed_effects_data, fixed_effects, random_effect, dependent_variables, output_filename='./tables/mixed_methods_all.tex')

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
    true_data = pd.read_csv('../parsed_data/mixed_effects_data.csv')

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
    with open(output_filename, "w") as f:
        f.write(table)
    print(f"Table saved to {output_filename}.")


if __name__ == '__main__':
    # make_csv()
    # output_mixed_effects_table()
    # perform_regression_analysis()
    output_all_regressions_in_one_table()
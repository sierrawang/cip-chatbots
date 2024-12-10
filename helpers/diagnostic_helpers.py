import json
import os
import numpy as np

# Return the diagnostic score for this student
# If the student did not take the diagnostic, impute their score with impute_val (default 0)
def get_student_diagnostic_score(user_id, impute_val=-1):
    student_results_filename = f'../downloaded_data/diagnostic/{user_id}.json'
    if os.path.exists(student_results_filename):
        # If the student took the diagnostic, calculate their score
        student_results = json.load(open(student_results_filename))
        
        # Keep track of their score on each question
        question_scores = []

        # Loop through each question and calculate the percent of the question that the student got correct
        for question in student_results:
            question_feedback = student_results[question]['gptFeedback']
            num_correct = 0

            # Check each rubric item
            for error in question_feedback:
                if question_feedback[error]['option'] == 0:
                    # They got it correct!
                    num_correct += 1

            # Calculate the percent of the question that the student got correct
            question_score = num_correct / len(question_feedback)
            question_scores.append(question_score)
        
        # Calculate the student's score as the average of their question scores
        student_score = np.mean(question_scores)
        return student_score
    else:
        # If the student did not take the diagnostic, impute their score with 0
        return impute_val

# Return a list of the diagnostic scores for each student in the given df
# impute_val is the value to use for students who did not take the diagnostic
# (default -1 means to exclude them from the analysis)
def get_diagnostic_scores(df, impute_val=-1):
    studentIds = df['user_id'].tolist()
    results = []
    for studentId in studentIds:
        # Compute the diagnostic score for this student
        student_score = get_student_diagnostic_score(studentId, impute_val)

        if student_score >= 0:
            # Append the diagnostic score for this student
            results.append(student_score)

    return results

# Return a list of the diagnostic participation for each student in the given df 
# (1 if they took the diagnostic, 0 otherwise)
def get_diagnostic_participation(df):
    user_ids = df['user_id'].unique()
    results = []
    for user_id in user_ids:
        # Check if the user has taken the diagnostic (../downloaded_data/diagnostic/{user_id}.json exists)
        if os.path.exists(f'../downloaded_data/diagnostic/{user_id}.json'):
            results.append(1)
        else:
            results.append(0)
    return results
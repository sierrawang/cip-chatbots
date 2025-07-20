import pandas as pd
import os
import numpy as np

def get_relative_filepath(filepath):
    current_dir = os.path.dirname(__file__)
    filepath = os.path.join(current_dir, filepath)
    return filepath

# Return the average number of times this student ran their code
# for an assignment
def get_avg_runs_per_assignment_per_user(user_id):
    ide_logs_filename = get_relative_filepath(
        f'../../downloaded_data/ide_logs_data/{user_id}.csv')
    if os.path.exists(ide_logs_filename):
        ide_logs = pd.read_csv(ide_logs_filename)

        # Group the logs by assnId
        grouped_logs = ide_logs.groupby('assnId')

        # Compute the average number of times this student ran 
        # their code for an assignment
        run_lengths = []
        for assnId, group in grouped_logs:
            run_lengths.append(len(group))

        # The user never ran their code for an assignment (can not use runs for code
        # without an assignment id because it could be for more than one project)
        if len(run_lengths) == 0:
            return 0

        return np.mean(run_lengths)
    
    else:
        # There are no logs for this user, so they never ran their code
        return 0

# Return the number of times this user visited the IDE according to the visit logs
def get_num_ide_visits_per_user(user_id):
    user_logs_filename = get_relative_filepath(
        '../../downloaded_data/visit_logs_data/' + user_id + '.csv')
    if os.path.exists(user_logs_filename):
        user_logs = pd.read_csv(user_logs_filename)
        ide_logs = user_logs[user_logs['path'].str.contains('/cip4/ide/')]
        return len(ide_logs)
    else:
        # There are no visit logs for this user, so they never visited the IDE
        return 0

# Return the number of times this user visited a lessons page
def get_num_lesson_visits_per_user(user_id):
    user_logs_filename = get_relative_filepath(
        '../../downloaded_data/visit_logs_data/' + user_id + '.csv')
    if os.path.exists(user_logs_filename):
        user_logs = pd.read_csv(user_logs_filename)
        lesson_logs = user_logs[user_logs['path'].str.contains('/cip4/learn/')]
        return len(lesson_logs)
    else:
        # There are no visit logs for this user, so they never visited the lessons
        return 0

# Return a list of the number of times each user visited the IDE
def get_num_ide_visits(df):
    res = []
    for index,row in df.iterrows():
        user_id = row['user_id']
        res.append(get_num_ide_visits_per_user(user_id))
    return res

# Return a list of the number of times each user visited the IDE
def get_num_lesson_visits(df):
    res = []
    for index,row in df.iterrows():
        user_id = row['user_id']
        res.append(get_num_lesson_visits_per_user(user_id))
    return res

# Return a list of the average number of times each user ran their code on an assignment
def get_avg_runs_per_assignment(df):
    res = []
    for _,row in df.iterrows():
        user_id = row['user_id']
        avg_num_runs = get_avg_runs_per_assignment_per_user(user_id)
        res.append(avg_num_runs)

    return res

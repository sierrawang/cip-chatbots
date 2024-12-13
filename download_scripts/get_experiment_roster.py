import pandas as pd
import os

def load_experiment_roster(roster_filename='../experiment_roster/experiment_rosters/experiment_roster_complete.csv'):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    roster_filename = os.path.join(current_dir, roster_filename)
    df = pd.read_csv(roster_filename)
    return df

# Get the user ids of all students in the experiment
def get_experiment_roster(roster_filename='../experiment_roster/experiment_rosters/experiment_roster_complete.csv'):
    experiment_roster = load_experiment_roster(roster_filename)
    return experiment_roster['user_id'].to_list()

def get_section_ids(roster_filename='../experiment_roster/experiment_rosters/experiment_roster_complete.csv'):
    experiment_roster = load_experiment_roster(roster_filename)
    section_ids = experiment_roster['section_id'].unique()
    return section_ids
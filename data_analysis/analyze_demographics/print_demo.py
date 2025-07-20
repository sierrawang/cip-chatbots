from data_analysis.helpers.rosters_helpers import get_student_data
from download_scripts.get_experiment_roster import load_experiment_roster

def print_num_students(student_data):
    print(len(student_data), 'students')

def print_num_countries(student_data):
    print(len(student_data['country'].unique()), 'countries')

if __name__ == '__main__':
    student_data = get_student_data()
    print_num_students(student_data)
    print_num_countries(student_data)

    experiment_roster = load_experiment_roster()
    print(experiment_roster['chatType'].value_counts())
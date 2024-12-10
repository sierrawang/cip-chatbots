import pandas as pd

# These were the constants used in the frontend to represent the different chat types.
# These are the chat types that are in the experiment roster.
NO_CHAT = 0
GROUNDED = 1
GROUNDED_PERSONIFIED = 2
BASIC = 3
BASIC_PERSONIFIED = 4
COMMUNITY = 5
COMMUNITY_PERSONIFIED = 6
BUTTONS = 7
BUTTONS_PERSONIFIED = 8
IDE = 9
IDE_PERSONIFIED = 10

# Return the demographic data of the students
def get_student_data():
    return pd.read_csv('../downloaded_data/student_data.csv')

# Return a dataframe of the experiment roster (user_id and chatType)
def get_experiment_roster():
    return pd.read_csv('../downloaded_data/experiment_roster.csv')

def get_no_chat_students():
    experiment_roster = get_experiment_roster()
    return experiment_roster[experiment_roster['chatType'] == NO_CHAT]

def get_basic_personified_students():
    experiment_roster = get_experiment_roster()
    return experiment_roster[experiment_roster['chatType'] == BASIC_PERSONIFIED]

def get_basic_nonpersonified_students():
    experiment_roster = get_experiment_roster()
    return experiment_roster[experiment_roster['chatType'] == BASIC]

def get_ide_personified_students():
    experiment_roster = get_experiment_roster()
    return experiment_roster[experiment_roster['chatType'] == IDE_PERSONIFIED]

def get_ide_nonpersonified_students():
    experiment_roster = get_experiment_roster()
    return experiment_roster[experiment_roster['chatType'] == IDE]

def get_buttons_personified_students():
    experiment_roster = get_experiment_roster()
    return experiment_roster[experiment_roster['chatType'] == BUTTONS_PERSONIFIED]

def get_buttons_nonpersonified_students():
    experiment_roster = get_experiment_roster()
    return experiment_roster[experiment_roster['chatType'] == BUTTONS]

def get_community_personified_students():
    experiment_roster = get_experiment_roster()
    return experiment_roster[experiment_roster['chatType'] == COMMUNITY_PERSONIFIED]

def get_community_nonpersonified_students():
    experiment_roster = get_experiment_roster()
    return experiment_roster[experiment_roster['chatType'] == COMMUNITY]

def get_grounded_personified_students():
    experiment_roster = get_experiment_roster()
    return experiment_roster[experiment_roster['chatType'] == GROUNDED_PERSONIFIED]

def get_grounded_nonpersonified_students():
    experiment_roster = get_experiment_roster()
    return experiment_roster[experiment_roster['chatType'] == GROUNDED]

def get_experiment_groups():
    experiment_groups = {
        'Basic/Agent': get_basic_personified_students(),
        'Basic/Tool': get_basic_nonpersonified_students(),
        'IDE/Agent': get_ide_personified_students(),
        'IDE/Tool': get_ide_nonpersonified_students(),
        'Grounded/Agent': get_grounded_personified_students(),
        'Grounded/Tool': get_grounded_nonpersonified_students(),
        'Community/Agent': get_community_personified_students(),
        'Community/Tool': get_community_nonpersonified_students(),
        'Buttons/Agent': get_buttons_personified_students(),
        'Buttons/Tool': get_buttons_nonpersonified_students(),
        'Control': get_no_chat_students()
    }
    return experiment_groups
from rosters_helpers import NO_CHAT, IDE_PERSONIFIED, IDE, GROUNDED, GROUNDED_PERSONIFIED, BUTTONS, BUTTONS_PERSONIFIED, COMMUNITY, COMMUNITY_PERSONIFIED

import sys
sys.path.insert(1, '../experiment_roster/scripts')
from create_experiment_roster import consistent_section_leader

def get_sl_id_from_stored(user_id, initial_section_membership):
    user_row = initial_section_membership[initial_section_membership['user_id'] == user_id]
    assert len(user_row) == 1
    return user_row['sl_id'].values[0]

# Return a list with a 1 for each student who changed sections, 
# and a 0 for each student who did not change sections
def get_changed_section(roster, initial_section_membership, section_membership_510, section_membership_519, section_membership_531):
    changed_section_results = []

    for _, row in roster.iterrows():
        user_id = row['user_id']
        sl_id = get_sl_id_from_stored(user_id, initial_section_membership)
        if consistent_section_leader(user_id, sl_id, section_membership_510, section_membership_519, section_membership_531):
            changed_section_results.append(0)
        else:
            changed_section_results.append(1)

    return changed_section_results
    
# Return a list with a 1 for each student who received an IDE chat, 
# and a 0 for each student who did not receive an IDE chat
def get_ide(roster):
    ide_results = []
    for _, row in roster.iterrows():
        if row['chatType'] == IDE or row['chatType'] == IDE_PERSONIFIED:
            ide_results.append(1)
        else:
            ide_results.append(0)

    return ide_results

# Return a list with a 1 for each student who received a RAG chat,
# and a 0 for each student who did not receive a RAG chat
def get_rag(roster):
    rag_results = []
    for _, row in roster.iterrows():
        if row['chatType'] == GROUNDED or row['chatType'] == GROUNDED_PERSONIFIED:
            rag_results.append(1)
        else:
            rag_results.append(0)

    return rag_results

# Return a list with a 1 for each student who received a community chat,
# and a 0 for each student who did not receive a community chat
def get_community(roster):
    community_results = []
    for _, row in roster.iterrows():
        if row['chatType'] == COMMUNITY or row['chatType'] == COMMUNITY_PERSONIFIED:
            community_results.append(1)
        else:
            community_results.append(0)

    return community_results

# Return a list with a 1 for each student who received a buttons chat,
# and a 0 for each student who did not receive a buttons chat
def get_buttons(roster):
    buttons_results = []
    for _, row in roster.iterrows():
        if row['chatType'] == BUTTONS or row['chatType'] == BUTTONS_PERSONIFIED:
            buttons_results.append(1)
        else:
            buttons_results.append(0)

    return buttons_results

# Return a list with a 1 for each student with a personified chat, 
# and a 0 for each student with a non-personified chat
# NOTE: The chatType will be even for personified chats, and odd for non-personified chats!
def get_personified(roster):
    personified_results = []
    for _, row in roster.iterrows():
        # assert row['chatType'] != NO_CHAT # This function should not be called for students with no chat!

        # If the chatType is even, the chat is personified
        if row['chatType'] % 2 == 0:
            personified_results.append(1)
        else:
            personified_results.append(0)

    return personified_results

# Return a list with a 1 for each female student, and a 0 for each non-female student
def get_female(roster, student_data):
    female_results = []

    for _, row in roster.iterrows():
        student_info = student_data[student_data['user_id'] == row['user_id']].iloc[0]
        if student_info['gender'] == 'female':
            female_results.append(1)
        else:
            female_results.append(0)

    return female_results

# Return a list with a 1 for each student in the USA, and a 0 for each student not in the USA
def get_in_usa(roster, student_data):
    in_usa_results = []

    for _, row in roster.iterrows():
        student_info = student_data[student_data['user_id'] == row['user_id']].iloc[0]
        if student_info['country'] == 'United States':
            in_usa_results.append(1)
        else:
            in_usa_results.append(0)

    return in_usa_results

# Return a list with the age of each student
def get_age(roster, student_data):
    age_results = []

    for _, row in roster.iterrows():
        student_info = student_data[student_data['user_id'] == row['user_id']].iloc[0]
        age_results.append(student_info['age'])

    return age_results
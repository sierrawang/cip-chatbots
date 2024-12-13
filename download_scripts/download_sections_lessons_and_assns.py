import os
import json
import csv
import multiprocessing
from get_experiment_roster import get_experiment_roster

import sys
sys.path.insert(1, '../utils')
import util

lesson_progress_folder = "../downloaded_data/lessons_progress/"
assn_progress_folder = "../downloaded_data/assn_progress/"

studentUserIds = get_experiment_roster()

# Delete and recreate the lesson_progress folder
def reset_lesson_progress_folder():
    # print("Resetting lesson_progress folder")
    if os.path.exists(lesson_progress_folder):
        os.system(f'rm -rf {lesson_progress_folder}')
    os.mkdir(lesson_progress_folder)

# Delete and recreate the assn_progress folder
def reset_assn_progress_folder():
    # print("Resetting assn_progress folder")
    if os.path.exists(assn_progress_folder):
        os.system(f'rm -rf {assn_progress_folder}')
    os.mkdir(assn_progress_folder)

# Download the lesson data for all students.
# Save the lesson data for each student to a json file lessons_progress/{userId}.json
# All data can be found in /users/{userId}/cip4/lessonsProgress
def download_lesson_data():
    # Get a reference to the db
    db = util.setup_db()
    
    # Iterate through all student userIds
    # studentUserIds = get_experiment_roster()

    for userId in studentUserIds:
        # Get the lessonsProgress
        lessonsProgressData = db.collection('users').document(userId).collection('cip4').document('lessonsProgress').get()
        if not lessonsProgressData.exists:
            continue

        lessonsProgress = lessonsProgressData.to_dict()

        # Make a list of all the lessonIds (all keys in the lessonsProgress dictionary)
        lessonsCompleted = list(lessonsProgress.keys())
        
        # Save the lessonsCompleted to a json file
        with open(f'{lesson_progress_folder}/{userId}.json', 'w') as f:
            json.dump(lessonsCompleted, f)

# Download the assignment data for all students.
# Save the assignment data for each student to a json file assn_progress/{userId}.json
# All data can be found in /users/{userId}/cip4/assnProgress
def download_assn_data():
    # Get a reference to the db
    db = util.setup_db()
    
    # Iterate through all student userIds
    # studentUserIds = get_experiment_roster()
    for userId in studentUserIds:
        # Get the assnProgress
        assnProgressData = db.collection('users').document(userId).collection('cip4').document('assnProgress').get()
        if not assnProgressData.exists:
            continue

        assnProgress = assnProgressData.to_dict()
        assnCompleted = list(assnProgress.keys())

        # Save the assnCompleted to a json file
        with open(f'{assn_progress_folder}/{userId}.json', 'w') as f:
            json.dump(assnCompleted, f)

# Download the section data for all students.
# Save the section data for each student to a csv file section_progress.csv
# The csv file will have the following columns:
# user_id, 0, 1, 2, 3, 4, 5
# All data can be found in /users/{userId}/cip4/sectionAttendance
def download_section_data():
    filename = '../downloaded_data/section_progress.csv'
    fieldnames = ['user_id', '0', '1', '2', '3', '4', '5']

    # Open the output file for writing
    f = open(filename, 'w')
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    # Get a reference to the db
    db = util.setup_db()

    # Iterate through all student userIds
    # studentUserIds = get_experiment_roster()
    for userId in studentUserIds:
        # Get the sectionAttendance
        sectionAttendanceData = db.collection('users').document(userId).collection('cip4').document('sectionAttendance').get()
        if not sectionAttendanceData.exists:
            continue

        sectionAttendance = sectionAttendanceData.to_dict()
        section_data = {section: sectionAttendance.get(section, False) for section in fieldnames[1:]}
        section_data['user_id'] = userId
        writer.writerow(section_data)

def download_sections_lessons_and_assns():
    processes = []
    data_download_functions = [download_lesson_data, download_assn_data, download_section_data]
    
    # Output the time 
    # print("Starting data download processes at: ", datetime.datetime.now())

    for function in data_download_functions:
        proc = multiprocessing.Process(target=function)
        processes.append(proc)
        proc.start()

    for proc in processes:
        proc.join()

    # Output the time
    # print("Finished data download processes at: ", datetime.datetime.now())

if __name__ == "__main__":
    reset_lesson_progress_folder()
    reset_assn_progress_folder()
    download_sections_lessons_and_assns()

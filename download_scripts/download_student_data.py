import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from get_experiment_roster import get_experiment_roster

import sys
sys.path.insert(1, '../utils')
import util

courseId = 'cip4'

output_folder = '../downloaded_data/student_data/'

fieldnames = ["user_id", "role", "gender", "age", "country", "occupation", "hometown", "timeAvailable", "learn", "community", "heardOf106a", "fun", "sectionLeader", "job", "newExperiment"]

def reset_user_data_folder():
    if os.path.exists(output_folder):
        os.system(f'rm -rf {output_folder}')
    os.mkdir(output_folder)

def get_role(user_id, db):
    roles = db.collection('users').document(user_id).collection('roles').document(courseId).get().to_dict()
    if roles:
        return roles['role']
    else:
        return None

def get_age(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection(courseId).document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection(courseId).document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            # Calculate age from birthday
            birthday = user_doc['dateOfBirth']
            # Make the start date 5-22-2024 at 12:00:00 AM UTC
            start_date = datetime(2024, 5, 22)
            birth_date = datetime(birthday['year'], birthday['month'], birthday['day'])
            age = start_date.year - birth_date.year - ((start_date.month, start_date.day) < (birth_date.month, birth_date.day))
            return age
        except:
            return -1
    else:
        return -1

def get_gender(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection(courseId).document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection(courseId).document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            return user_doc['gender']
        except:
            return None
    else:
        return None

def get_country(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection(courseId).document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection(courseId).document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            country_info = user_doc['country']
            return country_info['eng_name']
        except:
            return None
    else:
        return None

def get_occupation(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection(courseId).document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection(courseId).document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            return user_doc['currentOccupation']
        except:
            return None
    else:
        return None

def get_hometown(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection(courseId).document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection(courseId).document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            return user_doc['city']
        except:
            return None
    else:
        return None


def get_timeAvailable(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection(courseId).document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection(courseId).document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            return user_doc['timeAvailible']
        except:
            return None
    else:
        return None
    

def get_interest(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection(courseId).document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection(courseId).document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            return user_doc['interest']
        except:
            return {}
    else:
        return {}

# Helper function to process a single user's data
def process_user_data(userId, db):
    users_collection = db.collection('users')

    user_row = {'user_id': userId}
    user_row['role'] = 'student' # get_role(userId, db) 
    user_row['age'] = get_age(userId, users_collection, user_row['role'])
    user_row['gender'] = get_gender(userId, users_collection, user_row['role'])
    user_row['country'] = get_country(userId, users_collection, user_row['role'])
    user_row['occupation'] = get_occupation(userId, users_collection, user_row['role'])
    user_row['hometown'] = get_hometown(userId, users_collection, user_row['role'])
    user_row['timeAvailable'] = get_timeAvailable(userId, users_collection, user_row['role'])
    interest = get_interest(userId, users_collection, user_row['role'])
    user_row['learn'] = 'learn' in interest
    user_row['community'] = 'community' in interest
    user_row['heardOf106a'] = 'heardOf106a' in interest
    user_row['fun'] = 'fun' in interest
    user_row['sectionLeader'] = 'sectionLeader' in interest
    user_row['job'] = 'job' in interest
    user_row['newExperiment'] = 'newExperiment' in interest

    with open(output_folder + userId + '.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(user_row)

# Main function to download user info using parallel processing
def download_user_info():    
    db = util.setup_db()

    # Setup database and file writer
    studentUserIds = get_experiment_roster()

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks
        future_to_user = {executor.submit(process_user_data, userId, db): userId for userId in studentUserIds}
    
        # Wait for tasks to complete
        for future in as_completed(future_to_user):
            userId = future_to_user[future]
            try:
                future.result()
            except Exception as e:
                print(f"download_student_data: error processing user {userId}: {e}")

# Concate all user data into one file
def concat_user_data():
    filename = '../downloaded_data/student_data.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for userId in os.listdir(output_folder):
            with open(output_folder + userId, 'r') as user_file:
                reader = csv.DictReader(user_file)
                for row in reader:
                    writer.writerow(row)

if __name__ == "__main__":
    reset_user_data_folder()
    download_user_info()
    concat_user_data()
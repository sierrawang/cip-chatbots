from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from get_experiment_roster import get_experiment_roster
import json

import sys
sys.path.insert(1, '../utils')
import util

output_folder = '../downloaded_data/diagnostic/'

def reset_diagnostic_folder():
    print("Resetting diagnostic folder")
    if os.path.exists(output_folder):
        os.system(f'rm -rf {output_folder}')
    os.mkdir(output_folder)

def process_user_data(userId, db):
    userCollection = db.collection('diagnostic_feedback_v2').document('cip4').collection('users').document(userId)

    results = userCollection.get()
    if not results.exists:
        return
    else:
        with open(output_folder + f'{userId}.json', 'w', newline='') as f:
            json.dump(results.to_dict(), f)

# Download a csv with the firstVisit for every user
def download_diagnostic_results():
    print("Downloading diagnostic results")
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
                print(f"Error processing user {userId}: {e}")

if __name__ == "__main__":
    reset_diagnostic_folder()
    download_diagnostic_results()
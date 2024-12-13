import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import pandas as pd
from get_experiment_roster import get_section_ids

import sys
sys.path.insert(1, '../utils')
import util


output_folder = '../downloaded_data/forum_data/'

fieldnames = ['post_id', 'user_id', 'text', 'title', 'timestamp', 'numLikes', 'isDraft', 'isFlagged', 'isPinned', 'isPrivate', 'isResolved', 'parent_id']

def reset_forum_folder():
    print("Resetting forum data folder")
    if os.path.exists(output_folder):
        os.system(f'rm -rf {output_folder}')
    os.mkdir(output_folder)

def process_section_data(sectionId, message_type, db):
    postsCollection = db.collection('forumData').document('cip4').collection('forums').document(sectionId).collection(message_type)

    if not postsCollection.get():
        return

    with open(output_folder + f'{sectionId}_{message_type}.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for doc in postsCollection.stream():
            data = doc.to_dict()
            post_id = doc.id
            user_id = data.get('authorUid', '')
            contents = data.get('contents', {})
            text = contents.get('text', '')
            title = contents.get('title', '')
            timestamp = data.get('time', '')
            likedBy = data.get('likedBy', {})
            numLikes = len(likedBy)
            isDraft = data.get('isDraft', '')
            isFlagged = data.get('isFlagged', '')
            isPinned = data.get('isPinned', '')
            isPrivate = data.get('isPrivate', '')
            isResolved = data.get('isResolved', '')
            parent_id = data.get('parent', '')
            row = {
                'post_id': post_id,
                'user_id': user_id,
                'text': text,
                'title': title,
                'timestamp': timestamp,
                'numLikes': numLikes,
                'isDraft': isDraft,
                'isFlagged': isFlagged,
                'isPinned': isPinned,
                'isPrivate': isPrivate,
                'isResolved': isResolved,
                'parent_id': parent_id
            }
            writer.writerow(row)

def download_forum():
    print("Downloading forum data")
    db = util.setup_db()

    # Setup database and file writer
    section_ids = get_section_ids()
    section_ids = ['main'] + list(section_ids)

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks for posts
        future_to_user = {executor.submit(process_section_data, section_id, 'posts', db): section_id for section_id in section_ids}

        # Submit tasks for replies
        future_to_user.update({executor.submit(process_section_data, section_id, 'replies', db): section_id for section_id in section_ids})
    
        # Wait for tasks to complete
        for future in as_completed(future_to_user):
            section_id = future_to_user[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing section {section_id}: {e}")

if __name__ == "__main__":
    reset_forum_folder()
    download_forum()
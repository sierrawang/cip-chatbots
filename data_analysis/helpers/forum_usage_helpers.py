import pandas as pd
import os

def get_relative_filepath(filepath):
    current_dir = os.path.dirname(__file__)
    filepath = os.path.join(current_dir, filepath)
    return filepath

# Return the forum posts for the given user on the given forum
def get_forum_posts_for_user_on_forum(user_id, post_type, forum_id):
    forum_filename = get_relative_filepath(f'../../downloaded_data/forum_data/{forum_id}_{post_type}.csv')
    if not os.path.exists(forum_filename):
        print(f"File {forum_filename} does not exist")
        
        # Return an empty dataframe
        return pd.DataFrame()
    else:
        # Get the forum posts for this section
        forum_posts = pd.read_csv(
            get_relative_filepath(f'../../downloaded_data/forum_data/{forum_id}_{post_type}.csv'))

        # Get the forum posts by this user
        user_forum_posts = forum_posts[forum_posts['user_id'] == user_id]

        return user_forum_posts

def get_num_forum_posts_for_user_on_forum(user_id, post_type, forum_id):
    # Get the forum posts by this user
    user_forum_posts = get_forum_posts_for_user_on_forum(user_id, post_type, forum_id)
    
    return len(user_forum_posts)

def get_forum_posts_for_user(user_id, post_type, experiment_roster):
    # Get the section_id for this user
    section_id = experiment_roster[experiment_roster['user_id'] == user_id]['section_id'].values[0]
    section_forum_posts = get_forum_posts_for_user_on_forum(user_id, post_type, section_id)
    main_forum_posts = get_forum_posts_for_user_on_forum(user_id, post_type, 'main')
    user_forum_posts = pd.concat([section_forum_posts, main_forum_posts])
    return user_forum_posts

# Return the number of forum posts by the given user
# post_type is either 'posts' or 'replies'
def get_num_forum_posts_for_user(user_id, post_type, experiment_roster):
    # Get the section_id for this user
    user_forum_posts = get_forum_posts_for_user(user_id, post_type, experiment_roster)
    return len(user_forum_posts)

# Return a list of the number of forum posts by each student
def get_num_forum_posts(df, post_type, experiment_roster, include_all=True):
    user_ids = df['user_id'].unique()
    results = []
    for user_id in user_ids:
        # Get the number of forum posts by the user
        num_posts = get_num_forum_posts_for_user(user_id, post_type, experiment_roster)
        
        if include_all or (num_posts > 0):
            results.append(num_posts)
    return results

# Return a 1 if the user posted on the forum, and a zero otherwise
def get_user_made_post(user_id, post_type, experiment_roster):
    num_posts = get_num_forum_posts_for_user(user_id, post_type, experiment_roster)
    if num_posts > 0:
        return 1
    else:
        return 0

# Return a list of whether each student posted on the forum
def get_forum_participation(df, post_type, experiment_roster):
    user_ids = df['user_id'].unique()
    results = []
    for user_id in user_ids:
        results.append(get_user_made_post(user_id, post_type, experiment_roster))
    return results
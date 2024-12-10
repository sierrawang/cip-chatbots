import pandas as pd

def get_forum_posts_for_user_on_forum(user_id, post_type, forum_id):
    # Get the forum posts for this section
    forum_posts = pd.read_csv(f'../downloaded_data/forum_data/{forum_id}_{post_type}.csv')

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

# Return a list of whether each student posted on the forum
def get_forum_participation(df, post_type, experiment_roster):
    user_ids = df['user_id'].unique()
    results = []
    for user_id in user_ids:
        # Check if the user posted on the forum
        num_posts = get_num_forum_posts_for_user(user_id, post_type, experiment_roster)
        if num_posts > 0:
            results.append(1)
        else:
            results.append(0)
    return results
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from scipy import stats
import math

import sys
sys.path.insert(1, '../download_scripts')
from get_experiment_roster import load_experiment_roster
sys.path.append('../helpers')
from hdi_helpers import get_hdi
from chat_usage_helpers import get_chat_messages, get_num_messages_sent_for_user
from rosters_helpers import get_student_data, get_experiment_groups, get_ide_personified_students, get_ide_nonpersonified_students, get_buttons_personified_students, get_buttons_nonpersonified_students, get_community_personified_students, get_community_nonpersonified_students, get_basic_personified_students, get_basic_nonpersonified_students, get_no_chat_students

# Return a list of the number of messages sent by each student from the given country
def get_messages_for_country(country, student_data, chat_messages, key='country'):
    # Get the user_ids for students in this country
    user_ids = student_data[student_data[key] == country]['user_id']
    
    # Get the messages sent by students in this country
    messages_count = []
    for user_id in user_ids:
        num_msg = get_num_messages_sent_for_user(user_id, chat_messages)
        messages_count.append(num_msg)

    return messages_count

def get_roster():
    # experiment_roster = load_experiment_roster()
    ide_agent = get_ide_personified_students()
    ide_tool = get_ide_nonpersonified_students()
    ide_students = pd.concat([ide_agent, ide_tool])
    # return experiment_roster
    return ide_students

    # lessons_agent = get_basic_personified_students()
    # lessons_tool = get_basic_nonpersonified_students()
    # lessons_students = pd.concat([lessons_agent, lessons_tool])
    # return lessons_students

# Output the average number of messages sent by a student in each country
def avg_num_messages_by_country():
    # Load the data
    student_data = get_student_data()
    experiment_roster = get_roster()
    chat_messages = get_chat_messages()

    # Filter the student data to only include students in the experiment
    student_data = student_data[student_data['user_id'].isin(experiment_roster['user_id'])]

    # Get the number of messages sent by each student in each country
    countries = student_data['country'].unique()
    results = []

    for country in countries:
        messages_counts = get_messages_for_country(country, student_data, chat_messages)
        if len(messages_counts) < 5:
            # Skip countries with no students
            continue
        
        sent_message = np.count_nonzero(messages_counts) / len(messages_counts) * 100

        mean = 0
        if sent_message != 0:
            mean = sum(messages_counts) / np.count_nonzero(messages_counts)

        # sem = stats.sem(messages_counts)
        sem = -1 # Placeholder for now

        # print(country, mean, sem)
        results.append({
            'country': country, 
            'avg_message_count': mean, 
            'sem': sem, 
            'sent_message': sent_message,
            'num_students': len(messages_counts)
        })

    results_df = pd.DataFrame(results)
    return results_df

def avg_num_messages_by_gender():
    # Load the data
    student_data = get_student_data()
    experiment_roster = get_roster()
    chat_messages = get_chat_messages()

    # Filter the student data to only include students in the experiment
    student_data = student_data[student_data['user_id'].isin(experiment_roster['user_id'])]

    # Get the number of messages sent by each student in each country
    genders = student_data['gender'].unique()
    results = []

    for gender in genders:
        messages_counts = get_messages_for_country(gender, student_data, chat_messages, 'gender')
        # if len(messages_counts) < 5:
        #     # Skip countries with no students
        #     continue
        
        sent_message = np.count_nonzero(messages_counts) / len(messages_counts) * 100

        mean = 0
        if sent_message != 0:
            mean = sum(messages_counts) / np.count_nonzero(messages_counts)

        # sem = stats.sem(messages_counts)
        sem = -1 # Placeholder for now

        # print(country, mean, sem)
        results.append({
            'country': gender, 
            'avg_message_count': mean, 
            'sem': sem, 
            'sent_message': sent_message,
            'num_students': len(messages_counts)
        })

    results_df = pd.DataFrame(results)
    return results_df

def plot_choropleth_with_labels(results_df):
    # Create the base choropleth map
    fig = go.Figure(
        data=go.Choropleth(
            locations=results_df['country'],  # Column with country names
            locationmode='country names',    # Match country names
            z=results_df['mean'],            # Data to color by
            colorscale='blues',            # Color scale
            colorbar_title="Avg Messages"
        )
    )
    
    # Add labels
    for _, row in results_df.iterrows():
        fig.add_trace(
            go.Scattergeo(
                locationmode='country names',
                locations=[row['country']],
                text=f"{row['mean']:.0f}",  # Label content
                mode='text',
                textfont=dict(size=14, color="black"),  # Customize font
                showlegend=False
            )
        )
    
    # Set layout
    fig.update_layout(
        title="Average Messages Sent by Students per Country",
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
    )
    
    fig.show()

def bar_chart(results_df):
    # Sort the data by average messages
    sorted_df = results_df.sort_values(by='mean', ascending=False)

    plt.figure(figsize=(10, 8))
    sns.barplot(x='mean', y='country', data=sorted_df, palette='viridis')
    plt.xlabel("Average Messages Sent")
    plt.ylabel("Country")
    plt.title("Average Number of Messages Sent by Students per Country")
    plt.tight_layout()
    plt.show()

def output_latex_table(results_df, output_file='avg_messages_country.tex'):
    # Sort the data by average messages
    sorted_df = results_df.sort_values(by='sent_message', ascending=False)
    
    table_str = """\\begin{table}
\\centering
\\begin{tabularx}{\\columnwidth}{P{1.8cm} Y Y @{\\hskip 3mm} P{1.8cm} Y Y}
\\toprule
\\textbf{Country} & \\textbf{\\%} & \\textbf{\\#} & \\textbf{Country} & \\textbf{\\%} & \\textbf{\\#} \\\\
\\cmidrule(r{3mm}){1-3} \\cmidrule(l{0mm}){4-6} """

    num_rows = len(sorted_df)
    halfway = math.ceil(num_rows / 2)

    for index, (_, row) in enumerate(sorted_df.iterrows()):
        if index == halfway:
            break
        elif halfway + index < num_rows:
            # Add the current row, and the corresponding row from the second half
            second_half_row = sorted_df.iloc[halfway + index]
            table_str += f"\n{row['country']} ({row['num_students']}) & {row['sent_message']:.1f}\\% & {row['avg_message_count']:.1f} & {second_half_row['country']} ({second_half_row['num_students']}) & {second_half_row['sent_message']:.1f}\\% & {second_half_row['avg_message_count']:.1f} \\\\"
        else:
            # Add the current row
            table_str += f"\n{row['country']} & {row['sent_message']:.1f}\\% & {row['avg_message_count']:.1f} & & & \\\\"

    table_str += """
\\bottomrule
\\end{tabularx}
\\caption{Shows chat engagement by country --- specifically, the percent of students who sent a message to the chatbot (\\%) and the average number of messages that they sent (\\#). This table only includes students who received a chatbot in the IDE and countries with at least five such students.}
\\label{tab:avg_messages_country}
\\end{table}"""

    # print(table_str)
    with open(output_file, 'w') as f:
        f.write(table_str)
        print(f"Table written to {output_file}")

if __name__ == '__main__':
    # Get the averages by country
    # results_df = avg_num_messages_by_country()
    results_df = avg_num_messages_by_gender()

    # Plot the choropleth map with labels
    # plot_choropleth_with_labels(results_df)

    # Plot the bar chart
    # bar_chart(results_df)

    output_latex_table(results_df, 'avg_messages_gender.tex')
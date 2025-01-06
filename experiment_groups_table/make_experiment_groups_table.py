import numpy as np
import pandas as pd

import sys
sys.path.insert(1, '../download_scripts')
from get_experiment_roster import load_experiment_roster

sys.path.insert(1, '../helpers')
from chat_usage_helpers import get_chat_messages, get_message_sent_results, get_num_messages_sent_results
from rosters_helpers import get_experiment_groups, get_student_data
from course_completion_helpers import get_assignment_completion, get_lesson_completion, get_section_attendance
from diagnostic_helpers import  get_diagnostic_scores, get_diagnostic_participation
from forum_usage_helpers import get_forum_participation, get_num_forum_posts
from confounds_helpers import get_female, get_age, get_in_usa

def get_placement(group):
    return 0

def get_personification(group):
    return 0

def get_functionality(group):
    return 0

def load_metrics():
    chat_messages = get_chat_messages()
    experiment_roster = load_experiment_roster()
    student_data = get_student_data()
    metrics = {
        'Chatbot Details': {
            'Placement': (get_placement, False),
            'Personification': (get_personification, False),
            'Functionality': (get_functionality, False)
        },
        'Demographics': {
            'Female': (lambda res: get_female(res, student_data), True),
            'Age': (lambda res: get_age(res, student_data), False),
            'In USA': (lambda res: get_in_usa(res, student_data), True),
        },
        'Chat Usage': {
            'Sent Message': (lambda res: get_message_sent_results(res, chat_messages), True),
            'Message Count': (lambda res: get_num_messages_sent_results(res, chat_messages, False), False),
        },
        'Course Completion': {
            'Assn. Completion': (get_assignment_completion, True),
            'Lssn. Completion': (get_lesson_completion, True),
            'Sect. Attendance': (get_section_attendance, True),
        },
        'Forum Activity': {
            'Made Post': (lambda res: get_forum_participation(res, 'posts', experiment_roster), True),
            'Post Count': (lambda res: get_num_forum_posts(res,'posts', experiment_roster, False), False),
        },
        'Exam Performance': {
            'Took Exam': (get_diagnostic_participation, True),
            'Exam Score 1': (lambda res: get_diagnostic_scores(res, -1), True),
            'Exam Score 2': (lambda res: get_diagnostic_scores(res, 0), True),
        }
    }
    return metrics

# Output a table that has the details of each of the experiment groups
# There should be a column for each experiment group and a row for each metric
def output_table(output_filename):
    experiment_groups = get_experiment_groups()
    metrics = load_metrics()

    table_str = """\\begin{table*}[t]
\\begin{tcolorbox}[colback=cyan!5!white, colframe=teal!75!black, fonttitle=\\bfseries, title=Experiment Groups, boxrule=0.5mm, width=\\textwidth]
\\begin{center}
\\begin{tabularx}{\\textwidth}{l"""

    # Add a column for each experiment group
    for group in experiment_groups:
        table_str += "|X"
    table_str += "}\n"

    # Add the column headers
    table_str += f"\\textbf{{Metric}} "
    for group_name, roster in experiment_groups.items():
        table_str += f"& \\textbf{{{group_name}}}"
    table_str += "\\\\\n"

    # Add a row for each metric
    for category, engagement_metrics in metrics.items():
        table_str += f"\\hline\n\\multicolumn{{12}}{{l}}{{\\textbf{{{category}}}}} \\\\ \n"
        for metric_name, (engagement_fn, is_percent) in engagement_metrics.items():
            table_str += f"{metric_name} "
            for group_name, roster in experiment_groups.items():
                results = engagement_fn(roster)
                mean = np.mean(results)
                if is_percent:
                    mean = mean * 100
                    table_str += f" & {mean:.1f}\\%"
                else:
                    table_str += f" & {mean:.1f}"
            table_str += " \\\\\n"

    table_str += """ \\end{tabularx}
\\end{center}
\\end{tcolorbox}
\\caption{The chatbot configuration and number of students for each experiment group.}
\\label{tab:experiment-group-descriptions}
\\end{table*}"""

    # Save the table to a file
    with open(output_filename, 'w') as f:
        f.write(table_str)


if __name__ == '__main__':
    output_table('./tables/experiment_groups_table.tex')
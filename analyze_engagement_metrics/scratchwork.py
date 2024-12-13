import numpy as np
import pandas as pd

import sys
sys.path.insert(1, '../helpers')
from chat_usage_helpers import get_chat_messages, get_message_sent_results, get_num_messages_sent_results
from rosters_helpers import get_experiment_roster, get_basic_personified_students, get_basic_nonpersonified_students, get_ide_personified_students, get_ide_nonpersonified_students, get_no_chat_students, get_grounded_personified_students, get_grounded_nonpersonified_students, get_buttons_personified_students, get_buttons_nonpersonified_students, get_community_personified_students, get_community_nonpersonified_students
from course_completion_helpers import get_assignment_completion, get_lesson_completion, get_section_attendance
from diagnostic_helpers import  get_diagnostic_scores, get_diagnostic_participation
from forum_usage_helpers import get_forum_participation, get_num_forum_posts
from significance_helpers import bootstrap

def get_results(rosters, engagement_fn, is_percent=False):
    # Calculate the mean of each group
    first_roster_results = engagement_fn(rosters['Lessons'])
    second_roster_results = engagement_fn(rosters['IDE'])
    mean1, mean2, pval = bootstrap(first_roster_results, second_roster_results)

    if mean1 > mean2:
        if is_percent:
            mean1 = mean1 * 100
            mean2 = mean2 * 100
            return f'\\textbf{{{mean1:.1f}\\%}} & {mean2:.1f}\\% & {pval:.3f}'
        else:
            return f'\\textbf{{{mean1:.1f}}} & {mean2:.1f} & {pval:.3f}'
    else:
        if is_percent:
            mean1 = mean1 * 100
            mean2 = mean2 * 100
            return f'{mean1:.1f}\\% & \\textbf{{{mean2:.1f}\\%}} & {pval:.3f}'
        else:
            return f'{mean1:.1f} & \\textbf{{{mean2:.1f}}} & {pval:.3f}'

def output_table(rosters, engagement_categories, caption, label):
    table_str = f"""\\begin{{table}}[h!]
\\centering
\\begin{{tabularx}}{{\\columnwidth}}{{l Y Y Y}}
\\toprule
\\textbf{{Metric}} & \\textbf{{Lessons}} & \\textbf{{IDE}} & \\textbf{{p-value}} \\\\
"""
    for category, engagement_metrics in engagement_categories.items():
        table_str += f'\\midrule\n\\multicolumn{{4}}{{l}}{{\\textbf{{{category}}}}} \\\\\n'
        for metric_name, (engagement_fn, is_percent) in engagement_metrics.items():
            res_str1 = get_results(rosters, engagement_fn, is_percent)
            table_str += f'{metric_name} & {res_str1} \\\\\n'

    table_str += f"""\\bottomrule
\\end{{tabularx}}
\\caption{{{caption}}}
\\label{{{label}}}
\\end{{table}}"""
    
    print(table_str)

def lessons_vs_ide_table():
    engagement_metrics = load_engagement_metrics()
    basic_agent = get_basic_personified_students()
    basic_tool = get_basic_nonpersonified_students()
    lessons = pd.concat([basic_agent, basic_tool])

    ide_agent = get_ide_personified_students()
    ide_tool = get_ide_nonpersonified_students()
    ide = pd.concat([ide_agent, ide_tool])

    rosters = {
        "Lessons": lessons,
        "IDE": ide
    }
    # print(rosters)
    caption = f'TO DO'
    label = 'tab:to-do'

    output_table(rosters, engagement_metrics, caption, label)

def load_engagement_metrics():
    chat_messages = get_chat_messages()
    experiment_roster = get_experiment_roster()
    engagement_metrics = {
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
    return engagement_metrics

if __name__ == '__main__':
    lessons_vs_ide_table()





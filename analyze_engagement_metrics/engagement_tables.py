import numpy as np
import pandas as pd

import sys
sys.path.insert(1, '../download_scripts')
from get_experiment_roster import load_experiment_roster

sys.path.insert(1, '../helpers')
from chat_usage_helpers import get_chat_messages, get_message_sent_results, get_num_messages_sent_results
from rosters_helpers import get_basic_personified_students, get_basic_nonpersonified_students, get_ide_personified_students, get_ide_nonpersonified_students, get_student_data, get_no_chat_students, get_personified_students, get_nonpersonified_students
from course_completion_helpers import get_assignment_completion, get_lesson_completion, get_section_attendance
from diagnostic_helpers import  get_diagnostic_scores, get_diagnostic_participation
from forum_usage_helpers import get_forum_participation, get_num_forum_posts
from significance_helpers import bootstrap
from confounds_helpers import get_female, get_age, get_in_usa, get_personified, get_changed_section, get_ide, get_rag, get_community, get_buttons

sys.path.insert(1, '../experiment_roster/scripts')
from create_experiment_roster import load_initial_section_membership, load_section_membership_checkpoints

def get_results(roster1, roster2, engagement_fn, is_percent=False):
    # Calculate the mean of each group
    first_roster_results = engagement_fn(roster1)
    second_roster_results = engagement_fn(roster2)
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

def output_table(rosters, engagement_categories, caption, label, output_filename):
    table_str = f"""\\begin{{table}}
\\centering
\\begin{{tabularx}}{{\\columnwidth}}{{l X X X}}
\\toprule
\\textbf{{Metric}} & \\textbf{{{rosters[0][0]}}} & \\textbf{{{rosters[1][0]}}} & \\textbf{{p-value}} \\\\
"""

    for category, engagement_metrics in engagement_categories.items():
        table_str += f'\\midrule\n\\multicolumn{{4}}{{l}}{{\\textbf{{{category}}}}} \\\\\n'
        for metric_name, (engagement_fn, is_percent) in engagement_metrics.items():
            res_str1 = get_results(rosters[0][1], rosters[1][1], engagement_fn, is_percent)
            table_str += f'{metric_name} & {res_str1} \\\\\n'

    table_str += f"""\\bottomrule
\\end{{tabularx}}
\\caption{{{caption}}}
\\label{{{label}}}
\\end{{table}}"""
    
    with open(output_filename, 'w') as f:
        f.write(table_str)

    print(f"Table written to {output_filename}")

def control_table(output_filename='./tables/control_table.tex', label='tab:control-table'):
    engagement_metrics = load_engagement_metrics()
    basic_agent = get_basic_personified_students()
    basic_tool = get_basic_nonpersonified_students()
    baseline = pd.concat([basic_agent, basic_tool])
    control = get_no_chat_students()

    rosters = [
        ("Baseline", baseline),
        ("Control", control)
    ]

    caption = f'Compares students with a chatbot to those without a chatbot. For each comparison, the larger value is bold, and the p-value reflects the statistical significance of the differences.'

    output_table(rosters, engagement_metrics, caption, label, output_filename)

def lessons_vs_ide_table(output_filename='./tables/placement_table.tex', label='tab:placement-table'):
    engagement_metrics = load_engagement_metrics()
    basic_agent = get_basic_personified_students()
    basic_tool = get_basic_nonpersonified_students()
    lessons = pd.concat([basic_agent, basic_tool])

    ide_agent = get_ide_personified_students()
    ide_tool = get_ide_nonpersonified_students()
    ide = pd.concat([ide_agent, ide_tool])

    rosters = [
        ("Lessons", lessons),
        ("IDE", ide)
    ]

    caption = f'Compares students with a chatbot in the lessons interface to those with a chatbot in the IDE. For each comparison, the larger value is bold, and the p-value reflects the statistical significance of the differences.'

    output_table(rosters, engagement_metrics, caption, label, output_filename)

def agent_vs_tool_table(output_filename='./tables/personification_table.tex', label='tab:personification-table'):
    engagement_metrics = load_engagement_metrics()
    personified_students = get_personified_students()
    nonpersonified_students = get_nonpersonified_students()

    rosters = [
        ("Agent", personified_students),
        ("Tool", nonpersonified_students)
    ]

    caption = f'Compares students with an Agent chatbot to those with a Tool chatbot. For each comparison, the larger value is bold, and the p-value reflects the statistical significance of the differences.'
    
    output_table(rosters, engagement_metrics, caption, label, output_filename)

def load_engagement_metrics():
    chat_messages = get_chat_messages()
    experiment_roster = load_experiment_roster()
    student_data = get_student_data()
    initial_section_membership = load_initial_section_membership()
    section_membership_510, section_membership_519, section_membership_531 = load_section_membership_checkpoints()
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
        },
        'Confounds': {
            'Female': (lambda res: get_female(res, student_data), True),
            'Age': (lambda res: get_age(res, student_data), False),
            'In USA': (lambda res: get_in_usa(res, student_data), True),
            'Changed section': (lambda res: get_changed_section(res, initial_section_membership, section_membership_510, section_membership_519, section_membership_531), True),
            'IDE': (get_ide, True),
            'Agent': (get_personified, True),
            'RAG': (get_rag, True),
            'Community': (get_community, True),
            'Buttons': (get_buttons, True),
        }
    }
    return engagement_metrics

if __name__ == '__main__':
    control_table('./tables/control_table_complete.tex', 'tab:control-table-complete')
    agent_vs_tool_table('./tables/personification_table_complete.tex', 'tab:personification-table-complete')
    lessons_vs_ide_table('./tables/placement_table_complete.tex', 'tab:placement-table-complete')

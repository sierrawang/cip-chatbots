import numpy as np

import sys
sys.path.insert(1, '../helpers')
from chat_usage_helpers import get_chat_messages, get_message_sent_results, get_num_messages_sent_results
from rosters_helpers import get_experiment_roster, get_basic_personified_students, get_basic_nonpersonified_students, get_buttons_personified_students, get_buttons_nonpersonified_students, get_community_personified_students, get_community_nonpersonified_students, get_grounded_personified_students, get_grounded_nonpersonified_students, get_ide_personified_students, get_ide_nonpersonified_students
from course_completion_helpers import get_assignment_completion, get_lesson_completion, get_section_attendance
from diagnostic_helpers import  get_diagnostic_scores, get_diagnostic_participation
from forum_usage_helpers import get_forum_participation, get_num_forum_posts
from significance_helpers import bootstrap

def get_pair_results(rosters, engagement_fn, is_percent=False):
    # Calculate the mean of each group
    first_roster_results = engagement_fn(rosters['Agent'])
    second_roster_results = engagement_fn(rosters['Tool'])
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

def output_table(roster_sets, engagement_categories, caption, label):
    table_str = f"""\\begin{{table*}}[h!]
\\centering
\\begin{{tabularx}}{{\\textwidth}}{{l Y Y Y Y Y Y Y Y Y Y Y Y Y Y Y}}
\\toprule
"""
    
    for functionality, rosters in roster_sets.items():
        num_cols = len(rosters) + 1
        table_str += f' & \\multicolumn{{{num_cols}}}{{c}}{{\\textbf{{{functionality}}}}}'

    table_str += '\\\\\n\\cmidrule(lr){2-4} \\cmidrule(lr){5-7} \\cmidrule(lr){8-10} \\cmidrule(lr){11-13} \\cmidrule(lr){14-16} \n'

    # Add column headers
    table_str += '\\textbf{Metric} '
    for functionality, rosters in roster_sets.items():
        for name, _ in rosters.items():
            table_str += f'& \\textbf{{{name}}} '
        table_str += f'& \\textbf{{p-val}}'
    table_str += '\\\\\n'

    for category, engagement_metrics in engagement_categories.items():
        table_str += f'\\midrule\n\\multicolumn{{16}}{{l}}{{\\textbf{{{category}}}}} \\\\\n'
        for metric_name, (engagement_fn, is_percent) in engagement_metrics.items():
            table_str += f'{metric_name} '
            for functionality, rosters in roster_sets.items():
                res_str = get_pair_results(rosters, engagement_fn, is_percent)
                table_str += f'& {res_str} '
            table_str += '\\\\\n'

    table_str += f"""\\bottomrule
\\end{{tabularx}}
\\caption{{{caption}}}
\\label{{{label}}}
\\end{{table*}}"""
    
    print(table_str)

def personification_table():
    engagement_metrics = load_engagement_metrics()
    rosters = {
        'Basic (IDE)': {
            'Agent': get_ide_personified_students(),
            'Tool': get_ide_nonpersonified_students()
        },
        'Basic (Lessons)': {
            'Agent': get_basic_personified_students(),
            'Tool': get_basic_nonpersonified_students()
        },
        'RAG': {
            'Agent': get_grounded_personified_students(),
            'Tool': get_grounded_nonpersonified_students()
        },
        'Community': {
            'Agent': get_community_personified_students(),
            'Tool': get_community_nonpersonified_students()
        },
        'Buttons': {
            'Agent': get_buttons_personified_students(),
            'Tool': get_buttons_nonpersonified_students()
        }
    }
    caption = f'This table compares personifying the chatbot as an Agent versus as a Tool, in each placement (Lessons and IDE). The chatbot has Basic functionality in all cases. The metrics are described in Section \\ref{{sec:analysis-techniques}}. For each comparison, the larger value is bold, and the p-value shows the statistical significance of the observed difference.'
    label = 'tab:personification-metrics'

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
    personification_table()





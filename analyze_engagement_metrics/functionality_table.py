import numpy as np

import sys
sys.path.insert(1, '../helpers')
from chat_usage_helpers import get_chat_messages, get_message_sent_results, get_num_messages_sent_results
from rosters_helpers import get_experiment_roster, get_basic_personified_students, get_basic_nonpersonified_students, get_buttons_personified_students, get_buttons_nonpersonified_students, get_community_personified_students, get_community_nonpersonified_students, get_grounded_personified_students, get_grounded_nonpersonified_students
from course_completion_helpers import get_assignment_completion, get_lesson_completion, get_section_attendance
from diagnostic_helpers import  get_diagnostic_scores, get_diagnostic_participation
from forum_usage_helpers import get_forum_participation, get_num_forum_posts

def output_table(roster_sets, engagement_categories, caption, label):
    table_str = f"""\\begin{{table*}}[h!]
\\centering
\\begin{{tabularx}}{{\\textwidth}}{{l Y Y Y Y Y Y Y Y}}
\\toprule
"""
    
    for category, rosters in roster_sets.items():
        num_rosters = len(rosters)
        table_str += f' & \\multicolumn{{{num_rosters}}}{{c}}{{\\textbf{{{category}}}}}'

    table_str += '\\\\\n\\cmidrule(lr){2-5} \\cmidrule(lr){6-9} \n'

    table_str += '\\textbf{Metric} '
    for _, rosters in roster_sets.items():
        for name, _ in rosters.items():
            table_str += f'& \\textbf{{{name}}} '
    table_str += '\\\\\n'

    for category, engagement_metrics in engagement_categories.items():
        table_str += f'\\midrule\n\\multicolumn{{9}}{{l}}{{\\textbf{{{category}}}}} \\\\\n'
        for metric_name, (engagement_fn, is_percent) in engagement_metrics.items():
            table_str += f'{metric_name} '
            for _, rosters in roster_sets.items():
                results = []
                for _, df in rosters.items():
                    roster_results = engagement_fn(df)
                    mean = np.mean(roster_results)
                    results.append(mean)
                
                max_mean = max(results)
                for mean in results:
                    if is_percent:
                        mean_percent = mean * 100
                        if mean == max_mean:
                            table_str += f'& \\textbf{{{mean_percent:.1f}\\%}} '
                        else:
                            table_str += f'& {mean_percent:.1f}\\% '
                    else:
                        if mean == max_mean:
                            table_str += f'& \\textbf{{{mean:.1f}}} '
                        else:
                            table_str += f'& {mean:.1f} '
            table_str += '\\\\\n'

    table_str += f"""\\bottomrule
\\end{{tabularx}}
\\caption{{{caption}}}
\\label{{{label}}}
\\end{{table*}}"""
    
    print(table_str)

def functionality_table():
    engagement_metrics = load_engagement_metrics()
    rosters = {
        'Agent': {
            'Basic': get_basic_personified_students(),
            'RAG': get_grounded_personified_students(),
            'Community': get_community_personified_students(),
            'Buttons': get_buttons_personified_students(),
        },
        'Tool': {
            'Basic': get_basic_nonpersonified_students(),
            'RAG': get_grounded_nonpersonified_students(),
            'Community': get_community_nonpersonified_students(),
            'Buttons': get_buttons_nonpersonified_students()
        }
    }
    caption = f'This table compares the four different types of functionality for a chatbot (Basic, RAG, Community, and Buttons) for two levels of personification (Agent and Tool). The chatbot is placed in the lessons interface in all cases. The metrics are described in Section \\ref{{sec:analysis-techniques}}. For each four-way comparison, the largest value is bold.'
    label = 'tab:functionality-metrics'

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
    functionality_table()





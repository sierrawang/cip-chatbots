import numpy as np

import sys
sys.path.insert(1, '../helpers')
from chat_usage_helpers import get_chat_messages, get_message_sent_results, get_num_messages_sent_results
from rosters_helpers import get_experiment_roster, get_experiment_groups
from course_completion_helpers import get_assignment_completion, get_lesson_completion, get_section_attendance
from diagnostic_helpers import get_diagnostic_scores, get_diagnostic_participation
from forum_usage_helpers import get_forum_participation, get_num_forum_posts
from site_engagement_helpers import get_num_lesson_visits, get_num_ide_visits, get_avg_runs_per_assignment

def format_mean(mean, is_percent):
    if is_percent:
        mean = round(mean * 100, 3)
        mean_str = f"{mean}\\%"
    else:
        mean = round(mean, 3)
        mean_str = str(mean)

    return mean_str

def output_results_for_all_groups(metric_name, rosters, engagement_fn, is_percent):
    # Calculate the mean of each group
    means = []
    for _, df in rosters.items():
        results = engagement_fn(df)
        means.append(np.mean(results))

    # Construct the string to output by formatting all of the means
    result_str = f'{metric_name} '
    for mean in means:
        result_str += '& ' + format_mean(mean, is_percent) + ' '
    result_str += ' \\\\\n'
    return result_str

def print_header(rosters):
    header_str = """\\begin{table}[ht]
\centering
\\resizebox{\\columnwidth}{!}{
\\begin{tabular}{|c||c|c|c|c|c|c|c|c|c|c|c|c|c|}
\hline
\\textbf{Metric} """
    for name, _ in rosters.items():
        header_str += f'& \\textbf{{{name}}} '
    header_str += """\\\\
\\hline
"""
    print(header_str)

def print_footer(caption, label):
    print("""\\hline
\end{tabular}
}
\caption{""" + caption + """}
\label{tab:""" + label + """}
\end{table*}""")

def make_table(rosters, caption, label):
    print_header(rosters)

    # Construct the Course Completion results
    course_completion_str = '\hline\n'
    course_completion_str += '\multicolumn{12}{|c|}{\cellcolor{gray!20} Course Completion} \\\\\n'
    course_completion_str += '\hline\n'
    course_completion_str += output_results_for_all_groups('Assignment Completion', rosters, get_assignment_completion, True)
    course_completion_str += output_results_for_all_groups('Lesson Completion', rosters, get_lesson_completion, True)
    course_completion_str += output_results_for_all_groups('Section Attendance', rosters, get_section_attendance, True)
    course_completion_str += '\hline\n'
    print(course_completion_str)

    # Construct the Site Interaction results
    site_interaction_str = '\hline\n'
    site_interaction_str += '\multicolumn{12}{|c|}{\cellcolor{gray!20} Site Interaction} \\\\\n'
    site_interaction_str += '\hline\n'
    site_interaction_str += output_results_for_all_groups('Lesson Visits', rosters, get_num_lesson_visits, False)
    site_interaction_str += output_results_for_all_groups('IDE Visits', rosters, get_num_ide_visits, False)
    site_interaction_str += output_results_for_all_groups('Code Executions', rosters, get_avg_runs_per_assignment, False)
    site_interaction_str += '\hline\n'
    print(site_interaction_str)

    # Construct the Forum Activity results
    experiment_roster = get_experiment_roster()
    forum_activity_str = '\hline\n'
    forum_activity_str += '\multicolumn{12}{|c|}{\cellcolor{gray!20} Forum Activity} \\\\\n'
    forum_activity_str += '\hline\n'
    forum_activity_str += output_results_for_all_groups('Made Post (\% of Students)', rosters, lambda res: get_forum_participation(res, 'posts', experiment_roster), True)
    forum_activity_str += output_results_for_all_groups('\# Forum Posts', rosters, lambda res: get_num_forum_posts(res,'posts', experiment_roster, False), False)
    forum_activity_str += '\hline\n'
    print(forum_activity_str)

    # Construct the Diagnostic results
    diagnostic_str = '\hline\n'
    diagnostic_str += '\multicolumn{12}{|c|}{\cellcolor{gray!20} Exam Performance} \\\\\n'
    diagnostic_str += '\hline\n'
    diagnostic_str += output_results_for_all_groups('Exam Taken (\% of Students)', rosters, get_diagnostic_participation, True)
    diagnostic_str += output_results_for_all_groups('Exam Score (ignore missing)', rosters, lambda res: get_diagnostic_scores(res, -1), True)
    diagnostic_str += output_results_for_all_groups('Exam Score (impute missing)', rosters, lambda res: get_diagnostic_scores(res, 0), True)
    diagnostic_str += '\hline\n'
    print(diagnostic_str)

    # Construct the Chat usage results
    chat_messages = get_chat_messages()
    chat_str = '\hline\n'
    chat_str += '\multicolumn{12}{|c|}{\cellcolor{gray!20} Chat Usage} \\\\\n'
    chat_str += '\hline\n'
    chat_str += output_results_for_all_groups('Message Sent (\% of Students)', rosters, lambda res: get_message_sent_results(res, chat_messages), True)
    chat_str += output_results_for_all_groups('\# Messages Sent', rosters, lambda res: get_num_messages_sent_results(res, chat_messages, False), False)
    chat_str += '\hline\n'
    print(chat_str)

    print_footer(caption, label)

if __name__ == '__main__':
    experiment_groups = get_experiment_groups()

    make_table(experiment_groups, 'TO DO', 'engagement-all')
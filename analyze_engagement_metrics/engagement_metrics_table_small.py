import numpy as np

import sys
sys.path.insert(1, '../helpers')
from chat_usage_helpers import get_chat_messages, get_message_sent_results, get_num_messages_sent_results
from rosters_helpers import get_experiment_roster, get_basic_personified_students, get_basic_nonpersonified_students, get_ide_personified_students, get_ide_nonpersonified_students, get_no_chat_students
from course_completion_helpers import get_assignment_completion, get_lesson_completion, get_section_attendance
from diagnostic_helpers import  get_diagnostic_scores, get_diagnostic_participation
from forum_usage_helpers import get_forum_participation, get_num_forum_posts
from site_engagement_helpers import get_num_lesson_visits, get_num_ide_visits, get_avg_runs_per_assignment

def format_mean_green(mean, is_percent, rank):
    if is_percent:
        mean = round(mean * 100, 1)
        mean_str = f"{mean}\\%"
    else:
        mean = round(mean, 1)
        mean_str = str(mean)

    if rank == 0:
        return f"\\cellcolor{{darkestgreen}}{mean_str}"
    elif rank == 1:
        return f"\\cellcolor{{darkgreen}}{mean_str}"
    elif rank == 2:
        return f"\\cellcolor{{green}}{mean_str}"
    elif rank == 3:
        return f"\\cellcolor{{lightgreen}}{mean_str}"
    elif rank == 4:
        return f"\\cellcolor{{lightestgreen}}{mean_str}"

def output_results_for_all_groups(metric_name, rosters, engagement_fn, is_percent):
    # Calculate the mean of each group
    means = []
    for _, df in rosters.items():
        results = engagement_fn(df)
        means.append(np.mean(results))

    sorted_means = sorted(means, reverse=True)

    # Construct the string to output by formatting all of the means
    result_str = f'& {metric_name} '
    for mean in means:
        # result_str += '& ' + format_mean(mean, is_percent, min_value, max_value) + ' '
        result_str += '& ' + format_mean_green(mean, is_percent, sorted_means.index(mean)) + ' '
    result_str += ' \\\\\n'
    return result_str

def print_header(rosters):
    header_str = """\\begin{table}[ht]
\centering
\\resizebox{\\columnwidth}{!}{
\\renewcommand{\\arraystretch}{1.4}
\\begin{tabular}{|cc||c|c|c|c|c|}
\hline
\\textbf{Metric} """
    for name, _ in rosters.items():
        header_str += f'& \\textbf{{{name}}} '
    header_str += """\\\\
\\hline
Placement & IDE & IDE & Lessons & Lessons & - \\\\
Personification & Agent & Tool & Agent & Tool & - \\\\
\hline
"""
    print(header_str)

def print_footer(caption, label):
    print("""\\hline
\end{tabular}
}
\\includegraphics[width=\linewidth]{Images/engagement_table_legend.png}
\caption[]{""" + caption + """}
\label{tab:""" + label + """}
\end{table}""")

def make_table(rosters, caption, label):
    print_header(rosters)

    # Construct the Course Completion results
    course_completion_str = '\multicolumn{6}{|c|}{\cellcolor{gray!20} Course Completion} \\\\\n'
    course_completion_str += '\hline\n'
    course_completion_str += output_results_for_all_groups('Assn. Completion', rosters, get_assignment_completion, True)
    course_completion_str += output_results_for_all_groups('Less. Completion', rosters, get_lesson_completion, True)
    course_completion_str += output_results_for_all_groups('Sect. Attendance', rosters, get_section_attendance, True)
    course_completion_str += '\hline\n'
    print(course_completion_str)

    # Construct the Site Interaction results
    site_interaction_str = '\multicolumn{6}{|c|}{\cellcolor{gray!20} Site Interaction} \\\\\n'
    site_interaction_str += '\hline\n'
    site_interaction_str += output_results_for_all_groups('Lesson Visits', rosters, get_num_lesson_visits, False)
    site_interaction_str += output_results_for_all_groups('IDE Visits', rosters, get_num_ide_visits, False)
    site_interaction_str += output_results_for_all_groups('Code Executions', rosters, get_avg_runs_per_assignment, False)
    site_interaction_str += '\hline\n'
    print(site_interaction_str)

    # Construct the Forum Activity results
    experiment_roster = get_experiment_roster()
    forum_activity_str = '\multicolumn{6}{|c|}{\cellcolor{gray!20} Forum Activity} \\\\\n'
    forum_activity_str += '\hline\n'
    forum_activity_str += output_results_for_all_groups('\% Made Post', rosters, lambda res: get_forum_participation(res, 'posts', experiment_roster), True)
    forum_activity_str += output_results_for_all_groups('\# Posts', rosters, lambda res: get_num_forum_posts(res,'posts', experiment_roster, False), False)
    forum_activity_str += '\hline\n'
    print(forum_activity_str)

    # Construct the Diagnostic results
    diagnostic_str = '\multicolumn{6}{|c|}{\cellcolor{gray!20} Exam Performance} \\\\\n'
    diagnostic_str += '\hline\n'
    diagnostic_str += output_results_for_all_groups('\% Took Exam', rosters, get_diagnostic_participation, True)
    diagnostic_str += output_results_for_all_groups('Exam Score', rosters, lambda res: get_diagnostic_scores(res, -1), True)
    diagnostic_str += output_results_for_all_groups('Exam Score* \\tablefootnote{The average score of students in the group, imputing a zero score for each student who did not take the exam.}', rosters, lambda res: get_diagnostic_scores(res, 0), True)
    diagnostic_str += '\hline\n'
    print(diagnostic_str)

    # Construct the Chat usage results
    chat_messages = get_chat_messages()
    chat_str = '\multicolumn{6}{|c|}{\cellcolor{gray!20} Chat Usage} \\\\\n'
    chat_str += '\hline\n'
    chat_str += output_results_for_all_groups('\% Sent Message', rosters, lambda res: get_message_sent_results(res, chat_messages), True)
    chat_str += output_results_for_all_groups('\# Messages', rosters, lambda res: get_num_messages_sent_results(res, chat_messages, False), False)
    chat_str += '\hline\n'
    print(chat_str)

    print_footer(caption, label)

if __name__ == '__main__':
    basic_personified_students = get_basic_personified_students()
    basic_nonpersonified_students = get_basic_nonpersonified_students()
    ide_personified_students = get_ide_personified_students()
    ide_nonpersonified_students = get_ide_nonpersonified_students()
    control_students = get_no_chat_students()

    rosters = {
        'Group 1': ide_personified_students,
        'Group 2': ide_nonpersonified_students,
        'Group 3': basic_personified_students,
        'Group 4': basic_nonpersonified_students,
        'Control': control_students
    }

    caption = """Displays the outcomes for experiment Groups 1-4, which represent each combination of chat placement and personification, and have the same functionality.
`\% Made Post', `\% Took Exam', and `\% Sent Message' are the percentage of students who performed the task.
`\# Messages' and `\# Posts' are average counts for students who participated at least once, excluding those who never performed the task.
All other entries are the average per student in the group."""

    make_table(rosters, caption, 'engagement-metrics')
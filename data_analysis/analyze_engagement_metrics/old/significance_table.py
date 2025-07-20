import sys
sys.path.insert(1, '../helpers')
from chat_usage_helpers import get_chat_messages, get_message_sent_results, get_num_messages_sent_results
from rosters_helpers import get_experiment_roster, get_experiment_groups
from course_completion_helpers import get_assignment_completion, get_lesson_completion, get_section_attendance
from diagnostic_helpers import get_diagnostic_scores, get_diagnostic_participation
from forum_usage_helpers import get_forum_participation, get_num_forum_posts
from site_engagement_helpers import get_num_lesson_visits, get_num_ide_visits, get_avg_runs_per_assignment
from significance_helpers import bootstrap

def get_metrics():
    experiment_roster = get_experiment_roster()
    metrics = {
        'Assignment Completion': get_assignment_completion,
        'Lesson Completion': get_lesson_completion,
        'Section Attendance': get_section_attendance,
        'Lesson Visits': get_num_lesson_visits,
        'IDE Visits': get_num_ide_visits,
        'Code Executions': get_avg_runs_per_assignment,
        'Made Post (% of Students)': lambda res: get_forum_participation(res, 'posts', experiment_roster),
        '# Forum Posts': lambda res: get_num_forum_posts(res, 'posts', experiment_roster),
        'Took Exam (% of Students)': get_diagnostic_participation,
        'Exam Score (ignore missing)': lambda res: get_diagnostic_scores(res, -1),
        'Exam Score (impute missing)': lambda res: get_diagnostic_scores(res, 0)
    }

    return metrics

def print_header(metrics):
    header_str = """\\begin{table*}[ht]
\centering
\\begin{tabular}{\\textwidth}{|c||c|c|c|c|c|c|c|c|c|}
\hline
\\textbf{Pair} """
    for name, _ in metrics.items():
        header_str += f'& \\textbf{{{name}}} '
    header_str += '\\\\\n'
    header_str += '\\hline\n'
    print(header_str)

def print_footer(caption, label):
    print("""\\hline
\end{tabular}
\caption{""" + caption + """}
\label{tab:""" + label + """}
\end{table*}""")

def make_significance_table(rosters, metrics):
    # Calculate the results for all of the rosters
    roster_results = {}
    for name, roster in rosters.items():
        results = {}

        for metric, func in metrics.items():
            results[metric] = func(roster)

        roster_results[name] = results

    # Output the statistical significance between every combination of groups for each metric
    # The columns are the metrics
    # The rows are the pairs of groups
    roster_names = list(rosters.keys())
    for i in range(len(roster_names)):
        for j in range(i+1, len(roster_names)):
            # Initialize the line for the two groups
            line = f'{roster_names[i]} vs {roster_names[j]}'

            for metric,_ in metrics.items():
                # Get the results for the two groups
                results1 = roster_results[roster_names[i]][metric]
                results2 = roster_results[roster_names[j]][metric]

                if len(results1) == 0 or len(results2) == 0:
                    line += ' & -'
                else:
                    # Calculate the bootstrap results
                    _, _, pvalue = bootstrap(results1, results2)

                    # Add the p-value to the line
                    if pvalue < 0.05:
                        line += f' & \\textbf{{{pvalue:.3f}}}'
                    else:
                        line += f' & {pvalue:.3f}'
            
            line += ' \\\\'
            print(line)

def get_metrics():
    experiment_roster = get_experiment_roster()
    chat_messages = get_chat_messages()
    metrics = {
        'Assignment Completion': get_assignment_completion,
        'Lesson Completion': get_lesson_completion,
        'Section Attendance': get_section_attendance,
        'Lesson Visits': get_num_lesson_visits,
        'IDE Visits': get_num_ide_visits,
        'Code Executions': get_avg_runs_per_assignment,
        'Made Post (% of Students)': lambda res: get_forum_participation(res, 'posts', experiment_roster),
        '# Forum Posts': lambda res: get_num_forum_posts(res, 'posts', experiment_roster),
        'Took Exam (% of Students)': get_diagnostic_participation,
        'Exam Score (ignore missing)': lambda res: get_diagnostic_scores(res, -1),
        'Exam Score (impute missing)': lambda res: get_diagnostic_scores(res, 0),
        'Message Sent (\% of Students)': lambda res: get_message_sent_results(res, chat_messages),
        '\# Messages Sent': lambda res: get_num_messages_sent_results(res, chat_messages, False)
    }
    return metrics

if __name__ == '__main__':
    metrics = get_metrics()
    print_header(metrics)

    experiment_groups = get_experiment_groups()
    make_significance_table(experiment_groups, metrics)
    
    print_footer('Statistical Significance of Engagement Metrics', 'chatbot-significance')

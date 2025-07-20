import json
import os
import pandas as pd
from roadmap import all_assignments_in_order, all_lessons_in_order

# Return the percent of assignments completed by the given student
def get_student_assignment_completion(user_id, assignments_list=all_assignments_in_order):
    # Retrieve all of the assignments completed by this student
    userAssns = []
    student_assn_filename = f'../downloaded_data/assn_progress/{user_id}.json'
    if os.path.exists(student_assn_filename):
        userAssns = json.load(open(student_assn_filename))

    # Loop through every assignment and determine whether the student completed the assignment
    numCompleted = 0
    for assignment in assignments_list:
        if assignment in userAssns:
            numCompleted += 1
    
    # Append the percent of assignments completed by this student
    percentCompleted = numCompleted / len(assignments_list)
    return percentCompleted

# Return a list of the percent of assignments completed by each student in the given df
def get_assignment_completion(df, assignments_list=all_assignments_in_order):
    results = []
    studentIds = df['user_id'].tolist()
    for studentId in studentIds:
        # Get the percent of assignments completed by this student
        percentCompleted = get_student_assignment_completion(studentId, assignments_list)

        # Append this student's results to the list
        results.append(percentCompleted)

    # Return a list of the percent of assignments completed by each student in the given df
    return results

# Return the percent of lessons completed by the given student
def get_student_lesson_completion(user_id, lessons_list=all_lessons_in_order):
    # Retrieve all of the lessons completed by this student
    userLessons = []
    student_lessons_filename = f'../downloaded_data/lessons_progress/{user_id}.json'
    if os.path.exists(student_lessons_filename):
        userLessons = json.load(open(student_lessons_filename))

    # Loop through every lesson and determine the percent of the lesson that this student completed
    numCompleted = 0
    for lesson in lessons_list:
        lessonId = lesson[0]
        lessonParts = lesson[1]
        numParts = len(lessonParts)

        if lessonId in userLessons:
            # If the lessonId exists in the userLessons, then the student completed the lesson
            numCompleted += 1
        else:
            # Otherwise, calculate the percent of the lesson that the student completed
            partsCompleted = 0
            for part in userLessons:
                if part.startswith(f'{lessonId}/'):
                    partsCompleted += 1

            # Compute the percent of the lesson that the student completed
            percentLessonCompleted = partsCompleted / numParts

            # Add the percent of the lesson that the student completed to the total for this student
            numCompleted += percentLessonCompleted

    # Return the percent of lessons completed by the given student
    percentCompleted = numCompleted / len(lessons_list)
    return percentCompleted

# Return a list of the percent of lessons completed by each student in the given df
def get_lesson_completion(df, lessons_list=all_lessons_in_order):
    studentIds = df['user_id'].tolist()
    results = []

    for studentId in studentIds:
        # Compute the percent of lessons completed by this student
        percentCompleted = get_student_lesson_completion(studentId, lessons_list)

        # Append the percent of lessons completed by this student
        results.append(percentCompleted)

    # Return a list of the percent of lessons completed by each student in the given df
    return results

# Return the percent of sections attended by the given student
def get_student_section_attendance(user_id, section_attendance, weeks):
    totalSections = len(weeks)
    if user_id in section_attendance["user_id"].values:
        # Get the section attendance for this student
        userSections = section_attendance[section_attendance['user_id'] == user_id]
        numSections = 0
        for week in weeks:
            if userSections[str(week)].values[0]:
                numSections += 1

        # Append the percent of sections attended by this student
        percentSections = numSections / totalSections
        return percentSections
    else:
        # Assume the student attended 0 sections if we don't have a record for them
        return 0

# Return a list of the percent of sections of the given weeks 
# attended by each student in the given df
def get_section_attendance(df, weeks=[0, 1, 2, 3, 4, 5], section_attendance=None):
    studentIds = df['user_id'].tolist()
    results = []
    if section_attendance is None:
        section_attendance = pd.read_csv("../downloaded_data/section_progress.csv")
        
    for studentId in studentIds:
        # Compute the percent of sections attended by this student
        percentSections = get_student_section_attendance(studentId, section_attendance, weeks)

        # Append the percent of sections attended by this student
        results.append(percentSections)

    # Return a list of the percent of sections attended by each student in the given df
    return results

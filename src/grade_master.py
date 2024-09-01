#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GradeMaster: A flexible grading tool based on an answer key.
This script converts an answer key to a grading scheme, evaluates student data,
and generates feedback.

Usage:
    python grade_master.py answer_key_dir student_data_dir

Author: C. Ayala - ayalac@algonquincollege.com
Date: July 10th 2024
"""

import argparse
import logging
import os
import sys
import re
import yaml
from datetime import datetime
import csv
from tabulate import tabulate
from collections import OrderedDict


SPECIAL_CHAR = "#"

import yaml
from collections import OrderedDict

def represent_ordereddict(dumper, data):
    return dumper.represent_dict(data.items())

def parse_special_line(line):
    """
    Parses a line with special markers indicating points or keywords and their associated values.

    Args:
        line (str): The line to be parsed.

    Returns:
        tuple: A tuple containing either (points, value) or (keyword, value), or (None, None) if no match is found.

    """

    # match.group(1): Captures the points or keyword.
    # match.group(2): Captures the decimal part of the points (in the first regex) or the value (in the second regex).
    # match.group(3): Captures the value (in the first regex).

    # First regular expression pattern to match lines that start with #[<points>] <value>
    match = re.match(r"^#\[\s*(\d+(\.\d+)?)\s*\](.*)", line)
    # ^#\[ matches the beginning of the line followed by #[.
    # \s* matches any whitespace characters (spaces, tabs) zero or more times.
    # (\d+(\.\d+)?) captures one or more digits followed optionally by a decimal point and one or more digits,
    # representing the points.
    # This is captured in match.group(1).
    # \s* matches any whitespace characters zero or more times.
    # \] matches the closing ].
    # (.*) captures any remaining characters on the line as the value. This is captured in match.group(3).

    if match:
        # Group 1: The points value, which can be an integer or a float.
        # Group 3: The associated value or text.
        points = float(match.group(1).strip())
        value = match.group(3).strip()
        return points, value
    else:
        # Second regular expression pattern to match lines that start with #[<keyword>: <value>]
        match = re.match(r"^#\[\s*(\w+)\s*:\s*(.*?)\s*\]", line)
        # ^#\[ matches the beginning of the line followed by #[.
        # \s* matches any whitespace characters zero or more times.
        # (\w+) captures one or more word characters (letters, digits, underscores) as the keyword.
        # This is captured in match.group(1).
        # \s*:\s* matches a colon : surrounded by zero or more whitespace characters.
        # (.*?) captures any characters non-greedily as the value. This is captured in match.group(2).
        # \s* matches any whitespace characters zero or more times.
        # \] matches the closing ].
        if match:
            # Group 1: The keyword.
            # Group 2: The associated value or text.
            keyword = match.group(1).strip()
            value = match.group(2).strip()
            return keyword, value

    # Return (None, None) if no patterns match.
    return None, None


def convert_answer_key_to_yaml(answer_key_path, output_path):
    """
    Converts an answer key file to a YAML grading scheme.

    This function reads an answer key from a text file, processes its contents, and converts it into YAML format.
    The YAML file generated contains course information, lab details, professor name, total points, and a list of tasks,
    each with associated lines that include details, feedback, and points.

    Args:
        answer_key_path (str): The path to the answer key file.
        output_path (str): The path to the output YAML file.

    YAML Structure:
    ----------------
    The resulting YAML file will have the following structure:

    course: "Course Name"
    lab: "Lab Name"
    professor: "Professor Name"
    files: "Filename or NONE"
    total_points: float
    tasks:
      - task: "Task 1 Name"
        lines:
          - line: "Line to match"
            points: float
            detail: "Detail message"
            feedback: "Feedback message"
      - task: "Task 2 Name"
        lines:
          - line: "Another line to match"
            points: float
            detail: "Another detail message"
            feedback: "Another feedback message"


    TODO:
    -----
    - Implement support for multiple variables beyond just 'U' by modifying how `line` values are processed.
    - Adapt the function to handle AND/OR logic for more flexible grading, as outlined in the FEATURES.md.
    - Update the YAML structure to support additional fields if required (multi-file submissions).

    Note:
    -----
    If the "Multiple Variables from Student File" feature is implemented, this function will need to be adjusted
    to recognize and properly format these variables in the grading scheme. Additionally, the YAML structure might
    need to include metadata for these variables.

    """

    grading_scheme = OrderedDict([
        ("course", "NONE"),
        ("professor", "NONE"),
        ("lab", "NONE"),
        ("files", "NONE"),
        ("total_points", 0.0),
        ("tasks", [])
    ])
    current_task = None

    try:
        with open(answer_key_path, 'r') as file:
            # Read the first FIVE lines for course, lab, professor, and files
            # These lines should always be present in the answer_key
            for _ in range(5):
                line = file.readline().strip()
                if not line:
                    break
                keyword, value = parse_special_line(line)
                if keyword == "COURSE":
                    grading_scheme["course"] = value
                elif keyword == "LAB":
                    grading_scheme["lab"] = value
                elif keyword == "PROFESSOR":
                    grading_scheme["professor"] = value
                elif keyword == "FILES":
                    grading_scheme["files"] = value
                elif keyword == "TOTAL":
                    grading_scheme["total_points"] = float(value)

            # Process the remaining lines for tasks
            for line in file:
                line = line.strip()
                logging.debug(f"Processing line: {line}")
                if not line:
                    continue
                keyword, value = parse_special_line(line)
                if keyword:
                    logging.debug(f"Found keyword: {keyword}, value: {value}")
                    if keyword == "TASK":
                        if current_task:
                            grading_scheme["tasks"].append(current_task)

                        # Use OrderedDict to ensure "task" appears first, followed by "lines"
                        current_task = OrderedDict([
                            ("task", value),
                            ("lines", [])
                        ])
                    elif keyword == "DETAIL":
                        if current_task and current_task["lines"]:
                            current_task["lines"][-1]["detail"] = value
                    elif keyword == "FEEDBACK":
                        if current_task and current_task["lines"]:
                            current_task["lines"][-1]["feedback"] = value
                    else:
                        try:
                            points = float(keyword)
                            if current_task is not None:
                                current_task["lines"].append({
                                    "line": value,
                                    "points": points
                                })
                        except ValueError:
                            logging.warning(f"Unknown keyword or invalid points '{keyword}' in line: {line}")
            # Add the last task if it exists
            if current_task:
                grading_scheme["tasks"].append(current_task)

        logging.debug(f"Final grading scheme: {grading_scheme}")

        with open(output_path, 'w') as yamlfile:
            yaml.dump(grading_scheme, yamlfile, default_flow_style=False)

        logging.info(f"Successfully converted {answer_key_path} to {output_path}")

    except FileNotFoundError:
        logging.error(f"File not found: {answer_key_path}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def read_student_files(username, file_name, data_directory):
    """
    Reads the specific file for a student.

    This function constructs a filename based on the student's username and the specified file name. It then attempts to
    open and read the file from the given data directory. If the file is not found, it logs an error and returns an
    empty string.

    Args:
        username (str): The username of the student.
        file_name (str): The name of the file to read.
        data_directory (str): The directory where student files are located.

    Returns:
        str: The contents of the student's file.

    Usage:
    -------
    The function is typically used to read the configuration or submission files for a specific student,
    which are stored in a structured directory. For example:


    student_data = read_student_files("john_doe", "lab1.txt", "/path/to/student/files")

    The expected filename would be `john_doe-lab1.txt` located in the `/path/to/student/files/` directory.

    Logging:
    --------
    - Logs a debug message when it attempts to read the student's file.
    - Logs an error message if the file is not found.
    - Logs a debug message with the contents of the file (useful for troubleshooting).

    TODO:
    -----
    - Consider implementing additional error handling, such as checking for file read permissions.
    - If the "Multiple Variables from Student File" feature is implemented, this function might need to
      be adapted to handle reading multiple files associated with a single student.

    Note:
    -----
    - The function currently assumes a simple filename format (`username-file_name`). If the directory structure
      or naming convention changes, this function will need to be updated accordingly.

    """

    filename = f"{username}-{file_name}"
    logging.debug(f"Reading {username} file: {filename}")

    try:
        with open(os.path.join(data_directory, filename), 'r') as file:
            student_data = file.read()
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {filename}")
        student_data = ""

    logging.debug(f"{username} data for {filename}:  {student_data}")

    return student_data


def load_students(students_file):
    """
    Loads student data from a CSV file.

    This function reads a CSV file containing student information and returns a list of dictionaries,
    each representing a student with their corresponding username and UID. This data is essential
    for associating student submissions with their respective identifiers during the grading process.

    Args:
        students_file (str): The path to the students CSV file.

    Returns:
        list: A list of dictionaries with 'username' and 'uid'.
        Example:
              [
                  {'username': 'john_doe', 'uid': '1001'},
                  {'username': 'jane_smith', 'uid': '1002'},
                  ...
              ]

    YAML Structure:
    ----------------
    If the student data were to be represented in YAML format, it would look like the following:

    students:
      - username: "john_doe"
        uid: "1001"
      - username: "jane_smith"
        uid: "1002"
      # Additional student entries...

    This structure facilitates easy integration with other YAML-based configurations and tools.

    Usage:
    -------
    The function is typically used at the beginning of the grading script to load all student information
    before processing their submissions. For example:

    students = load_students("path/to/students.csv")
    for student in students:
        username = student['username']
        uid = student['uid']
        # Proceed with grading the student's submissions

    Logging:
    --------
    - Logs an error message if the CSV file cannot be found or read.
    - Logs debug messages for each student loaded (optional, depending on logging level).

    TODO:
    -----
    - Enhance error handling to manage malformed CSV files or missing headers.
    - Implement support for additional student attributes beyond 'username' and 'uid'.
    - Integrate validation to ensure that each student entry contains the required fields.

    Note:
    -----
    - If the "Multiple Variables from Student File" feature is implemented, this function will need to be
      updated to read and process additional columns from the `students.csv` file. This may involve dynamically
      handling varying numbers of attributes per student and ensuring that the grading scheme can utilize these
      additional variables effectively.
    - Ensure that the CSV file follows a consistent structure to prevent errors during parsing. If the directory
      structure or naming conventions for student files change, corresponding updates may be required in how
      student data is utilized throughout the grading script.
    """
    students = []
    with open(students_file, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            username = row[0]
            uid = row[1] if len(row) > 1 else 'NONE'
            students.append({'username': username, 'uid': uid})
    return students


def match_line(student_line, answer_key_line):
    """
    Matches a student's line with the answer key line using regular expressions.

    Args:
        student_line (str): The line from the student's data.
        answer_key_line (str): The regular expression from the answer key.

    Returns:
        bool: True if the student's line matches the answer key line, False otherwise.
    """

    # Adjust the pattern to handle spaces and optionally trailing characters

    answer_key_line = re.sub(r'\s+', r'\\s*', answer_key_line)

        # Add debug logging to see what is being matched
    logging.debug(f"Matching pattern: {answer_key_line}")
    logging.debug(f"Against line: {student_line}")

    # Perform the regex search
    match = re.search(answer_key_line, student_line)

    # Log the result of the match
    if match:
        logging.debug(f"\n------------->Match found: {match.group(0)}")
    else:
        logging.debug("No match found")

    return match is not None


def preprocess_line_for_student(line, student):
    """
    Replaces '{U}' and '{USERNAME}' in the line with the student's UID and username,
    and strips any extra spaces from the input strings.

    Args:
        line (str): The line to process.
        student (dict): The student dictionary containing 'username' and 'uid'.

    Returns:
        str: The processed line.
    """
    uid = student.get('uid', None)
    username = student.get('username', None)
    line = line.strip()
    if uid is not None:
        line = line.replace('{U}', str(uid).strip())
    if username is not None:
        line = line.replace('{USERNAME}', str(username).strip())
    return line


def update_general_feedback(general_feedback, student_feedback, grading_scheme):
    """
    Updates the general feedback structure with the results from a student's feedback.

    Args:
        general_feedback (dict): The general feedback structure.
        student_feedback (dict): The feedback from a single student.
        grading_scheme (dict): The grading scheme containing tasks and lines to match.
    """

    general_feedback["total_students"] += 1

    if "passing_students" not in general_feedback:
        general_feedback["passing_students"] = 0

    for student_task_feedback in student_feedback["feedback"]:
        task_name = student_task_feedback["task"]
        scores = student_task_feedback["score"]

        # Find or create the task feedback in general feedback
        task_feedback = next((task for task in general_feedback["tasks"] if task["task"] == task_name), None)
        if task_feedback is None:
            task_feedback = {
                "task": task_name,
                "scores": [0.0] * len(scores),
                "task_total_points": 0.0,
                "task_earned_points": 0.0,
                "task_average_score": 0.0,
                "task_average_rate": 0.0,
            }
            general_feedback["tasks"].append(task_feedback)

        # Find the corresponding task in the grading scheme
        grading_task = next((task for task in grading_scheme["tasks"] if task["task"] == task_name), None)
        if grading_task:
            # Update the scores
            for i, score in enumerate(scores):
                task_feedback["scores"][i] += score
                task_feedback["task_earned_points"] += score
                task_feedback["task_total_points"] += grading_task["lines"][i]["points"]

    # Calculate overall total points for all tasks
    total_points = sum(line["points"] for task in grading_scheme["tasks"] for line in task["lines"])
    # total_points = sum(task["task_total_points"] for task in general_feedback["tasks"])
    general_feedback["total_points"] = total_points

    # Calculate average score and rate for each task
    for task_feedback in general_feedback["tasks"]:
        task_feedback["task_average_score"] = round(task_feedback["task_earned_points"] / general_feedback["total_students"], 2)
        task_feedback["task_average_rate"] = round((task_feedback["task_earned_points"] / task_feedback["task_total_points"]) * 100, 2)

    # Calculate overall average score
    total_earned_points = sum(task["task_earned_points"] for task in general_feedback["tasks"])
    general_feedback["total_score"] = total_earned_points
    general_feedback["average_score"] = round(total_earned_points / general_feedback["total_students"] if general_feedback["total_students"] > 0 else 0, 2)

    # Calculate pass rate
    student_total_score = student_feedback["earned_points"]

    if student_total_score >= 0.5 * total_points:
        general_feedback["passing_students"] += 1

    general_feedback["pass_rate"] = round(general_feedback["passing_students"] / general_feedback["total_students"], 2)


def evaluate_student_data(student, student_data, grading_scheme):
    """
    Evaluates the student's data against the grading scheme.

    Args:
        student (dict): The student dictionary containing 'username', 'uid', and other potential details.
        student_data (str): The student's data.
        grading_scheme (dict): The grading scheme containing tasks and lines to match.

    Returns:
        dict: The evaluation results, including total points and feedback.
    """

    if not student_data.strip():
        return None

    results = {
        "total_points": 0.0,
        "earned_points": 0.0,
        "feedback": []
    }

    uid = student.get('uid', 'NONE')

    for task in grading_scheme["tasks"]:
        task_feedback = {
            "task": task["task"],
             "correctness": [],
            "score": []
        }

        for line in task["lines"]:
            answer_key_line = preprocess_line_for_student(line["line"], student)
            points = line["points"]

            results["total_points"] += points

            if any(match_line(student_line, answer_key_line) for student_line in student_data.splitlines()):
                results["earned_points"] += points
                task_feedback["correctness"].append(1)
                task_feedback["score"].append(points)
            else:
                task_feedback["correctness"].append(0)
                task_feedback["score"].append(0)

        results["feedback"].append(task_feedback)

    return results


def save_student_feedback(student, results, grading_scheme, output_dir, output_format="yaml"):
    """
    Saves feedback for the student in a text file using the tabulate package.

    Args:
        results (dict): The evaluation results.
        grading_scheme (dict): The grading scheme.
        student (dict): A dictionary with 'username' and 'uid'.
        output_dir (str): The directory where the feedback file should be saved.
        output_format(str):  Desired output format.
    """
    # Extract course, lab, and professor information from the grading scheme
    course = grading_scheme.get('course', 'Unknown Course')
    lab = grading_scheme.get('lab', 'Unknown Lab')
    professor = grading_scheme.get('professor', 'Unknown Professor')

    feedback_filename = f"{student['username']}-feedback"
    feedback_filepath = os.path.join(output_dir, feedback_filename)

    if results is None:
        # file.write("No submission or empty submission\n")
        logging.info(f"No submission or empty submission for student {student['username']}")
        return

    processed_feedback = []
    for task_result in results['feedback']:
        task_name = task_result.get('task', 'Unknown Task')
        scores = task_result.get('score', [])

        # Find the task in the grading scheme
        grading_task = next((task for task in grading_scheme["tasks"] if task["task"] == task_name), None)
        if grading_task:
            details = [line.get("detail", "") for line in grading_task["lines"]]
            feedbacks = [line.get("feedback", "") for line in grading_task["lines"]]

            task_feedback = {
                "task": task_name,
                "results": []
            }

            for i, score in enumerate(scores):
                detail = details[i] if i < len(details) else ''
                feedback = feedbacks[i] if i < len(feedbacks) else ''

                # Replace {U} with the student's UID in details and feedbacks if UID is not NONE
                # Use the preprocess_line_for_student function
                detail = preprocess_line_for_student(detail, student)
                feedback = preprocess_line_for_student(feedback, student)
                # if student.get('uid') and student['uid'] != 'NONE':
                #    detail = detail.replace("{U}", student['uid'])
                #    feedback = feedback.replace("{U}", student['uid'])

                if score == 1:
                    task_feedback["results"].append(detail)
                else:
                    task_feedback["results"].append(feedback)

            processed_feedback.append(task_feedback)

    if output_format == "yaml":
        # Prepare the YAML structure
        feedback_data = OrderedDict([
            ("course", [
                {"course_name": course},
                {"professor": professor}
            ]),
            ("lab", [
                {"lab_name": lab},
                {"graded_on": datetime.now().strftime('%a %d %b %Y %H:%M:%S %Z')},
                {"earned_points": results.get('earned_points', 0)},
                {"total_points": grading_scheme.get('total_points', 0)},
            ]),
            ("student", student),
            ("feedback", processed_feedback),
        ])

        # Save feedback as YAML
        with open(f"{feedback_filepath}.yaml", 'w') as file:
            yaml.dump(feedback_data, file, default_flow_style=False)
        logging.info(f"Feedback saved to {feedback_filepath}.yaml")

    else:  # Default to text format
        with open(f"{feedback_filepath}.txt", 'w') as file:
            file.write(f"{course} - {lab}\n")
            file.write(f"+{'-' * 68}+\n")
            file.write(f"|  Marked on {datetime.now().strftime('%a %d %b %Y %H:%M:%S %z')}\n")
            file.write(f"|  Marked by {professor}\n")
            file.write(f"|  Student ID {student['username']}\n")
            file.write(f"+{'-' * 68}+\n\n")

            headers = ["Task", "Detail/Feedback", "Earned", "Points"]
            table = []

            # Add logging to debug the structure of the results
            logging.debug(f"Results structure: {results}")

            for task_result in processed_feedback:
                task_name = task_result['task']
                task_details = task_result['results']

                for i, detail_or_feedback in enumerate(task_details):
                    row = [
                        task_name if i == 0 else '',  # Only show the task name once
                        detail_or_feedback,  # Show detail or feedback
                        results['earned_points'] if i == 0 else '',  # Only show earned points once per task
                        results['total_points'] if i == 0 else ''  # Only show total points once per task
                    ]
                    table.append(row)
                    task_name = ''  # Only show the task name once

                table.append(["", "", "", ""])

            # Add a separator line and total and earned points at the end
            table.append(["", "", "", ""])
            table.append(["Total Points", "", results['earned_points'], results['total_points']])

            # Write the table to the file with column alignment
            file.write(
                tabulate(table, headers=headers, tablefmt="pretty", colalign=("left", "left", "center", "center")))

        logging.debug(f"Feedback saved to {feedback_filepath}.txt")


def save_student_results_to_csv(student, results, lab_name, output_dir):
    """
    Save the student's results to a CSV file.

    Args:
        student (dict): A dictionary with 'username' and 'uid'.
        results (dict): The evaluation results.
        lab_name (str): The name of the lab.
        output_dir (str): The directory where the results file should be saved.
    """
    csv_file = os.path.join(output_dir, f"{lab_name}-grades.csv")

    # Check if the file already exists
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Write header if the file doesn't exist
            writer.writerow(['username', 'earned_points'])

        # Ensure results is not None and has 'earned_points'
        earned_points = results['earned_points'] if results and 'earned_points' in results else 0

        # Write the student's result
        writer.writerow([student['username'], results['earned_points']])
        # writer.writerow([f'#{student['username']}, {results['earned_points']}#'])

    logging.debug(f"Results saved to {csv_file}")


def parse_arguments():
    parser = argparse.ArgumentParser(description='GradeMaster: A flexible grading tool based on an answer key.')
    parser.add_argument('root_dir', type=str, help='The root directory for the course.')
    parser.add_argument('lab', type=str, help='The lab number or name.')
    return parser.parse_args()


def main():
    """
    Main function to run the GradeMaster script.
    Parses arguments,
    validates directories and files,
    converts the answer key to a YAML grading scheme,
    load all students from the csv file with their variables
    For each student
        load student data,
        evaluates their data against grading scheme,
        update general feedback
        saves student feedback
    save general feedback
    """

    # Parse arguments
    args = parse_arguments()

    root_dir = args.root_dir
    lab_name = args.lab

    # Set up logging
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    yaml.add_representer(OrderedDict, represent_ordereddict)

    lab_dir = os.path.join(root_dir, 'Labs', lab_name)
    submissions_dir = os.path.join(lab_dir, 'submissions')
    feedback_dir = os.path.join(lab_dir, 'feedback')
    answer_key_file = f"{lab_name}_answer_key.txt"
    grades_file = f"{lab_name}_grades.csv"
    grading_scheme_file = f"{lab_name}_grading_scheme.yaml"

    # Validate directories and files
    if not os.path.isdir(lab_dir):
        logging.error(f"The lab directory '{lab_dir}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(submissions_dir):
        logging.error(f"The submissions directory '{submissions_dir}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(feedback_dir):
        os.makedirs(feedback_dir)

    answer_key_path = os.path.join(lab_dir, answer_key_file)
    if not os.path.isfile(answer_key_path):
        logging.error(f"The answer key file '{answer_key_path}' does not exist.")
        sys.exit(1)

    students_file = os.path.join(root_dir, 'students.csv')
    if not os.path.isfile(students_file):
        logging.error(f"The students.csv file '{students_file}' does not exist.")
        sys.exit(1)

    logging.info(f"All required files are present in '{lab_dir}' and '{submissions_dir}' directories.")

    # Convert answer_key.txt to grading_scheme.yaml
    grading_scheme_path = os.path.join(lab_dir, grading_scheme_file)

    convert_answer_key_to_yaml(answer_key_path, grading_scheme_path)

    # Load grading scheme
    with open(grading_scheme_path, 'r') as yamlfile:
        grading_scheme = yaml.safe_load(yamlfile)

    # Load students
    students = load_students(students_file)

    # Read and process student files
    file_name = grading_scheme.get("files")
    if file_name == "NONE":
        logging.error("No FILES keyword found in the answer_key.")
        sys.exit(1)

        # Initialize general feedback
    general_feedback = {
        "total_students": 0,
        "average_score": 0,
        "pass_rate": 0,
        "tasks": []
    }

    for student in students:
        username = student['username']
        # uid = student['uid']

        # Load student data
        student_data = read_student_files(username, file_name, submissions_dir)

        # Evaluate the student's data
        results = evaluate_student_data(student, student_data, grading_scheme)

        logging.debug(f"Results for student {username}: {results}")

        # Save student feedback only if results are not None
        if results:
            save_student_feedback(student, results, grading_scheme, feedback_dir, output_format="yaml")
            update_general_feedback(general_feedback, results, grading_scheme)
            save_student_results_to_csv(student, results, lab_name, lab_dir)
        else:
            logging.info(f"No submission or empty submission for student {username}")
            save_student_results_to_csv(student, {"earned_points": 0}, lab_name, lab_dir)

    # Save general feedback to a file
    general_feedback_file = os.path.join(lab_dir, f'{lab_name}_general_feedback.yaml')
    with open(general_feedback_file, 'w') as yamlfile:
        yaml.dump(general_feedback, yamlfile, default_flow_style=False)


if __name__ == "__main__":
    main()

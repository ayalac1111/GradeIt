#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GradeIt: A flexible grading tool based on an answer key.
This script converts an answer key to a grading scheme, evaluates student data,
and generates feedback.

Usage:
    python grade_it.py answer_key_dir student_data_dir

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
from collections import OrderedDict


# Script constants
SPECIAL_CHAR = "#"
COMMENT_IDENTIFIER = "!--"
VALID_KEYWORDS = ["COURSE", "LAB", "PROFESSOR", "TOTAL", "FILE", "TASK", "DETAIL", "FEEDBACK"]


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
    match = re.match(r"^#\[\s*(\d+(\.\d+)?)\s*](.*)", line)
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
        match = re.match(r"^#\[\s*(\w+)\s*:\s*(.*?)\s*]", line)
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


def convert_answer_key_to_yaml(answer_key_file, output_path):
    """
    Converts an answer key file to a YAML grading scheme.

    This function reads an answer key from a text file, processes its contents, and converts it into YAML format.
    The YAML file generated contains course information, lab details, professor name, total points, and a list of tasks,
    each with associated lines that include details, feedback, and points.

    Args:
        answer_key_file (str): The path to the answer key file.
        output_path (str): The path to the output YAML file.

    YAML Structure:
    ----------------
    The resulting YAML file will have the following structure:

    course: "Course Name"
    lab: "Lab Name"
    professor: "Professor Name"
    total_points: float
    student_data:
      - filename: "{username}-01-file.txt"
        tasks:
          - task: "Task 1 Name"
            lines:
              - line: "Line to match"
                points: float
                detail: "Detail message"
                feedback: "Feedback message"
            task: "Task 2 Name"
            lines:
              - line: "Another line to match"
                points: float
                detail: "Another detail message"
                feedback: "Another feedback message"


    TODO:
    -----
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
        ("total_points", 0.0),
        ("grading_structure", [])
    ])

    current_file = None
    current_task = None

    try:
        with open(answer_key_file, 'r') as file:
            # Read the first FOUR lines for course, lab, professor, and files
            # These lines should always be present in the answer_key
            for _ in range(4):
                line = file.readline().strip()
                # Skip empty lines or comment lines
                if not line or line.startswith(COMMENT_IDENTIFIER):
                    logging.debug(f"Skipping line: {line}")
                    continue
                keyword, value = parse_special_line(line)
                if keyword == "COURSE":
                    grading_scheme["course"] = value
                elif keyword == "LAB":
                    grading_scheme["lab"] = value
                elif keyword == "PROFESSOR":
                    grading_scheme["professor"] = value
                elif keyword == "TOTAL":
                    grading_scheme["total_points"] = float(value)

            # Process the remaining lines for grading_scheme
            for line in file:
                line = line.strip()
                # Skip empty lines or comment lines
                if not line or line.startswith(COMMENT_IDENTIFIER):
                    logging.debug(f"Skipping line: {line}")
                    continue
                logging.debug(f"Processing line: {line}")

                keyword, value = parse_special_line(line)

                if keyword:
                    logging.debug(f"Found keyword: {keyword}, value: {value}")
                    if keyword == "FILE":
                        # If we have an existing file entry, save it to grading_structure
                        if current_task:
                            current_file["tasks"].append(current_task)
                            current_task = None
                        # If we have an existing file entry, save it to grading_structure
                        if current_file:
                            grading_scheme["grading_structure"].append(current_file)

                        # Create a new file entry
                        current_file = OrderedDict([
                            ("filename", value),
                            ("tasks", [])
                        ])
                    elif keyword == "TASK":
                        if current_task:
                            current_file["tasks"].append(current_task)

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
                        # Inside the loop processing grading_scheme lines in convert_answer_key_to_yaml

                        # Existing code:
                        # try:
                        #     points = float(keyword)
                        #     if current_task is not None:
                        #         current_task["lines"].append({
                        #             "line": value,
                        #             "points": points
                        #         })
                        # except ValueError:
                        #     logging.warning(f"Unknown keyword or invalid points '{keyword}' in line: {line}")

                        # Modified code to support composite conditions:
                        try:
                            points = float(keyword)
                            if current_task is not None:
                                # Check if the value ends with a composite operator
                                if value.rstrip().endswith("&&") or value.rstrip().endswith("||"):
                                    # Determine the operator based on the trailing characters
                                    operator = "AND" if value.rstrip().endswith("&&") else "OR"
                                    # Remove the trailing operator from the current line
                                    # Here, we split off the operator and trim any trailing whitespace
                                    condition = value.rstrip()[:-2].rstrip()
                                    patterns = [condition]

                                    # Now, read subsequent lines to complete the composite condition.
                                    # Each continued line that ends with the composite operator signals another pattern.
                                    while True:
                                        next_line = next(file, None)
                                        if not next_line:
                                            break  # End of file
                                        next_line = next_line.strip()
                                        # Skip empty or comment lines
                                        if not next_line or next_line.startswith(COMMENT_IDENTIFIER):
                                            continue
                                        if next_line.endswith("&&") or next_line.endswith("||"):
                                            # Ensure the operator is consistent
                                            op = "AND" if next_line.endswith("&&") else "OR"
                                            if op != operator:
                                                logging.error("Composite operator mismatch in answer key.")
                                            # Remove the trailing operator and add this pattern
                                            pattern = next_line[:-2].rstrip()
                                            patterns.append(pattern)
                                            # Continue reading if the next line is also part of the composite
                                            continue
                                        else:
                                            # This is the final line of the composite block; add it and break.
                                            patterns.append(next_line)
                                            break

                                    # Append a composite condition entry with an operator and list of patterns.
                                    current_task["lines"].append({
                                        "operator": operator,
                                        "patterns": patterns,
                                        "points": points
                                    })
                                else:
                                    # Otherwise, treat this as a simple condition.
                                    current_task["lines"].append({
                                        "line": value,
                                        "points": points
                                    })
                        except ValueError:
                            logging.warning(f"Unknown keyword or invalid points '{keyword}' in line: {line}")

            # Append the last task and file if they exist
            if current_task and current_file:
                current_file["tasks"].append(current_task)

            if current_file:
                grading_scheme["grading_structure"].append(current_file)

        logging.debug(f"Final grading scheme: {grading_scheme}")

        with open(output_path, 'w') as yamlfile:
            yaml.dump(grading_scheme, yamlfile, default_flow_style=False, allow_unicode=True)

        logging.info(f"Successfully converted {answer_key_file} to {output_path}")

    except FileNotFoundError:
        logging.error(f"File not found: {answer_key_file}")
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
        student_data = None

    logging.debug(f"{username} data for {filename}:  {student_data}")

    return student_data


def load_students(grade_it_paths):
    """
    Loads student data from a CSV file and handles malformed rows gracefully.
    Returns both student data and a list of valid variables to be used when grading.


    This function reads a CSV file containing student information, validates each row against the header fields,
    and skips any rows that do not match the expected format.

    Args:
        grade_it_paths (dict): Configuration paths containing the path to the students.csv file.

    Returns:
        list: A list of dictionaries where each dictionary represents a student and includes all attributes
              specified in the CSV file.

        tuple: A tuple containing:
            - A list of dictionaries representing student data.
            - A list of valid variables from the CSV headers.

        Example:
              [
                  {'username': 'john_doe', 'u': '1001', 'group': 'A'},
                  {'username': 'jane_smith', 'u': '1002', 'group': 'B'},
                  ...
              ]

    Note:
    -----
    - The function dynamically converts all CSV column headers to lowercase for consistency when creating
      the student dictionary. This ensures that the grading scheme can utilize these attributes effectively
      even if there are variations in column header formatting.
    - Summary of the Behavior:
        Extra fields in the row ➔ Ignored and the student is graded with the available data.
        Missing fields in the row ➔ Error is logged, and the student is skipped.
    """

    students_file = grade_it_paths['students_file']
    students = []

    with open(students_file, 'r') as file:
        csv_reader = csv.DictReader(file)

        # Normalize and clean headers, removing any empty headers
        normalized_headers = [header.strip().lower() for header in csv_reader.fieldnames if header.strip()]

        logging.debug(f"Validated headers found in CSV: {normalized_headers}")

        if 'username' not in normalized_headers:
            logging.error("The CSV file must contain a 'username' column in the header.")
            raise ValueError("Missing 'username' column in the student CSV file header.")

        for row_number, row in enumerate(csv_reader, start=2):  # start=2 accounts for the header row being row 1
            # Filter the row to include only keys that are in normalized_headers
            student = {key.lower(): row[key].strip() for key in normalized_headers if key in row and row[key].strip()}

            # Check for missing fields
            missing_fields = [key for key in normalized_headers if key not in row or not row[key].strip()]
            if missing_fields:
                logging.error(f"Row {row_number} is missing fields: {missing_fields}. Skipping this row.")
                continue  # Skip the row if it doesn't match the expected format

            logging.debug(f"Student dictionary created for row {row_number}: {student}")
            students.append(student)

    logging.info(f"Loaded {len(students)} students from {students_file}")
    return students, normalized_headers


def preprocess_line_for_student(line, student):
    """
    Replaces placeholders in the line with the student's data based on the CSV header.

    Args:
        line (str): The line to process.
        student (dict): The student dictionary containing  at least 'username'

    Returns:
        str: The processed line.
    """

    for key, value in student.items():
        placeholder = f"{{{key.upper()}}}"      # Use uppercases for placeholders in answer_key
        line = line.replace(placeholder, str(value).strip())

    return line


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
    match = re.search(answer_key_line, student_line, re.DOTALL)

    # Log the result of the match
    if match:
        logging.debug(f"\n------------->Match found: {match.group(0)}")
    else:
        logging.debug("No match found")

    return match is not None


def update_general_feedback(general_feedback, student_feedback, grading_scheme):
    """
    Updates the general feedback structure with the results from a student's feedback.

    Args:
        general_feedback (dict): The general feedback structure.
        student_feedback (dict): The feedback from a single student.
        grading_scheme (dict): The grading scheme containing tasks and lines to match.
    """

    logging.info(f"Total results content: {student_feedback}")

    # Since the student feedback contains score without the information of the grading scheme task, then
    # load the grading_scheme to correlate task and scores.
    task_earned_points = 0
    grading_structure = grading_scheme["grading_structure"]

    # Update number of students - should count all students even the ones with empty feedbacks
    general_feedback["total_students"] += 1

    # The student feedback is empty, then skip
    if student_feedback is None:
        general_feedback["no_submission"] = general_feedback.get("no_submission", 0) + 1
        return

    # Update the general_feedback with the new student feedback
    for student_task_feedback in student_feedback["feedback"]:
        logging.info(f"Adding feedback for student task: {student_task_feedback}")

        task_name = student_task_feedback["task"]
        scores = student_task_feedback["score"]

        # Reset for each task
        task_earned_points = 0

        # Find or create the task feedback in general feedback
        task_feedback = next((task for task in general_feedback["tasks"] if task["task"] == task_name), None)
        if task_feedback is None:
            task_feedback = {
                "task": task_name,
                "task_scores": [0.0] * len(scores),
                "task_average_score": 0.0,
            }
            logging.info(f"Task Feedback: {task_feedback}")
            general_feedback["tasks"].append(task_feedback)
            logging.info(f"General eedback: {general_feedback}")

        # Find the corresponding task in the grading scheme
        for file_data in grading_structure:
            grading_task = next((task for task in file_data["tasks"] if task["task"] == task_name), None)
            task_earned_points = 0
            if grading_task:
                # Update the scores
                for i, score in enumerate(scores):
                    task_feedback["task_scores"][i] += score
                    task_earned_points += score

    # Calculate overall total points for all tasks
    total_points = grading_scheme["total_points"]

    # Calculate average score and rate for each task
    for task_feedback in general_feedback["tasks"]:
        # Calculate total earned points for the task
        task_earned_points = sum(task_feedback["task_scores"])

        # Calculate the average score for the task as a percentage of the total possible points
        task_total_points = sum(task_feedback.get("total_possible_points", []))

        # Calculate the average score for the task
        if task_total_points > 0:
            task_feedback["task_average_score"] = round((task_earned_points / task_total_points) * 100, 2)
        # task_feedback["task_average_score"] = round(task_earned_points / general_feedback["total_students"] * 100, 2)

    # Calculate overall average score
    total_earned_points = sum(task_earned_points for task in general_feedback["tasks"])
    general_feedback["average_score"] = round(
        total_earned_points / general_feedback["total_students"] if general_feedback["total_students"] > 0 else 0, 2
    )

    # Calculate pass rate
    student_total_score = student_feedback["earned_points"]

    if student_total_score >= 0.5 * total_points:
        general_feedback["passing_students"] += 1

    general_feedback["pass_rate"] = round(
        general_feedback["passing_students"] / general_feedback["total_students"], 2)


def evaluate_student_data(student, student_file_data, tasks):
    """
    Evaluates the student's data against the grading scheme.

    Args:
        student (dict): The student dictionary containing 'username', 'uid', and other potential details.
        student_file_data (str): The student's data from the specific file.
        tasks (list): The tasks associated with the current file being evaluated.

    Returns:
        dict: The evaluation results, including total points and feedback.
    """

    logging.info(f"Evaluating {student['username']} for the provided tasks")

    if not student_file_data.strip():
        logging.info("Nothing to report")
        return None

    results = {
        "total_points": 0.0,
        "earned_points": 0.0,
        "feedback": []
    }

    for task in tasks:
        task_feedback = {
            "task": task["task"],
            "correctness": [],
            "score": []
        }

        for line in task["lines"]:
            points = line["points"]
            results["total_points"] += points

            # If no composite operator is present, evaluate as a simple condition
            if "operator" not in line:
                answer_key_line = preprocess_line_for_student(line["line"], student)
                if any(match_line(student_line, answer_key_line)
                       for student_line in student_file_data.splitlines()):
                    results["earned_points"] += points
                    task_feedback["correctness"].append(1)
                    task_feedback["score"].append(points)
                else:
                    task_feedback["correctness"].append(0)
                    task_feedback["score"].append(0)
            else:
                # Composite condition evaluation
                operator = line["operator"]
                patterns = line["patterns"]
                if operator == "AND":
                    composite_match = all(
                        any(match_line(student_line, preprocess_line_for_student(pattern, student))
                            for student_line in student_file_data.splitlines())
                        for pattern in patterns
                    )
                elif operator == "OR":
                    composite_match = any(
                        any(match_line(student_line, preprocess_line_for_student(pattern, student))
                            for student_line in student_file_data.splitlines())
                        for pattern in patterns
                    )
                else:
                    # Fallback: if operator is not recognized, treat as a failed match.
                    composite_match = False

                if composite_match:
                    results["earned_points"] += points
                    task_feedback["correctness"].append(1)
                    task_feedback["score"].append(points)
                else:
                    task_feedback["correctness"].append(0)
                    task_feedback["score"].append(0)

        # Append the aggregated task_feedback after processing all lines in the task.
        results["feedback"].append(task_feedback)

    # Log the final evaluation results for debugging
    logging.info("Evaluation results: %s", results)

    return results


def save_student_feedback(student, results, grading_scheme, output_dir):
    """
    Saves feedback for the student in a text file or YAML format.

    Args:
        results (dict): The evaluation results (None if no submission).
        grading_scheme (dict): The grading scheme.
        student (dict): A dictionary with 'username' and 'uid'.
        output_dir (str): The directory where the feedback file should be saved.
    """
    # Extract course, lab, and professor information from the grading scheme

    course = grading_scheme.get('course', 'Unknown Course')
    lab = grading_scheme.get('lab', 'Unknown Lab')
    professor = grading_scheme.get('professor', 'Unknown Professor')

    feedback_filename = f"{student['username']}-{lab}-feedback"
    feedback_filepath = os.path.join(output_dir, feedback_filename)

    grading_structure = grading_scheme["grading_structure"]

    # Initialize feedback_data with default values
    feedback_data = OrderedDict([
        ("course", [
            {"course_name": course},
            {"professor": professor}
        ]),
        ("lab", [
            {"lab_name": lab},
            {"graded_on": datetime.now().strftime('%a %d %b %Y %H:%M:%S %Z')},
            {"earned_points": 0},
            {"total_points": grading_scheme.get('total_points', 0)},
            {"lab_grade": "0%"}
        ]),
        ("student", student),
        ("feedback", "No submission found or incorrect submission format.")
    ])

    # If there are results, update the feedback_data
    if results:
        # Calculate earned points, total points, and lab grade
        earned_points = results.get('earned_points', 0)
        total_points = grading_scheme.get('total_points', 0)
        lab_grade = (earned_points / total_points) * 100 if total_points > 0 else 0

        processed_feedback = []
        for task_result in results['feedback']:
            task_name = task_result.get('task', 'Unknown Task')
            correctness = task_result.get('correctness', [])

            # Iterate over files in grading_structure to find the correct task details
            for file_data in grading_structure:
                grading_task = next((task for task in file_data["tasks"] if task["task"] == task_name), None)
                if grading_task:
                    details = [line.get("detail", "") for line in grading_task["lines"]]
                    feedbacks = [line.get("feedback", "") for line in grading_task["lines"]]

                    task_name = preprocess_line_for_student(task_name, student)
                    task_feedback = OrderedDict([
                        ("task", task_name),
                        ("results", [])
                    ])

                    for i, correct in enumerate(correctness):
                        detail = details[i] if i < len(details) else ''
                        feedback = feedbacks[i] if i < len(feedbacks) else ''

                        # Replace {VARIABLES}
                        detail = preprocess_line_for_student(detail, student)
                        feedback = preprocess_line_for_student(feedback, student)

                        task_feedback["results"].append(detail if correct == 1 else feedback)

                    processed_feedback.append(task_feedback)

        # Update feedback_data with results
        feedback_data["lab"][2]["earned_points"] = earned_points
        feedback_data["lab"][3]["total_points"] = total_points
        feedback_data["lab"][4]["lab_grade"] = f"{round(lab_grade, 2)}%"
        feedback_data["feedback"] = processed_feedback

    # Save feedback as YAML
    with open(f"{feedback_filepath}.yaml", 'w') as file:
        yaml.dump(feedback_data, file, default_flow_style=False, allow_unicode=True)
    logging.info(f"Feedback saved to {feedback_filepath}.yaml")


def save_student_results_to_csv(student, results, paths):
    """
    DEPRECATED
    Save the student's results to a CSV file.

    Args:
        student (dict): A dictionary with student information.
        results (dict): The evaluation results.
        paths (dict):
    """
    csv_file = paths["grades_csv_file"]

    # Check if the file already exists
    file_exists = os.path.isfile(csv_file)

    # Ensure results is not None and set earned_points to 0 if results is None
    earned_points = results['earned_points'] if results is not None and 'earned_points' in results else 0

    with (open(csv_file, 'a', newline='') as file):
        writer = csv.writer(file)
        if not file_exists:
            # Write header if the file doesn't exist
            writer.writerow(['username', 'earned_points'])

        # Write the student's result
        writer.writerow([student['username'], earned_points])

    logging.debug(f"Results saved to {csv_file}")


def configure_globals():
    """Sets up logging and YAML configuration."""

    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S')
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    yaml.add_representer(OrderedDict, represent_ordereddict)


def validate_directories_and_files(grade_it_paths):
    """
    Validates that all necessary directories and files exist based on the paths provided in grade_it_paths.

    Args:
        grade_it_paths (dict): Dictionary containing paths to directories and files that need to be validated.

    Raises:
        SystemExit: If any of the required directories or files do not exist.
    """

    # Validate submissions directory
    if not os.path.isdir(grade_it_paths['submissions_dir']):
        logging.error(f"The submissions directory '{grade_it_paths['submissions_dir']}' does not exist.")
        sys.exit(1)

    # Validate feedback directory, create it if it doesn't exist
    if not os.path.isdir(grade_it_paths['feedback_dir']):
        logging.info(f"The feedback directory '{grade_it_paths['feedback_dir']}' does not exist. Creating it.")
        os.makedirs(grade_it_paths['feedback_dir'])

    # Validate answer key file
    if not os.path.isfile(grade_it_paths['answer_key_file']):
        logging.error(f"The answer key file '{grade_it_paths['answer_key_file']}' does not exist.")
        sys.exit(1)

    # Validate students CSV file
    if not os.path.isfile(grade_it_paths['students_file']):
        logging.error(f"The students.csv file '{grade_it_paths['students_file']}' does not exist.")
        sys.exit(1)

    logging.info(f"All required files and directories are present.")
    return True


def extract_grading_scheme_variables(grading_scheme_content):
    """
    Extracts variables from the grading scheme content that are referenced within braces {}.

    Args:
        grading_scheme_content (str): The content of the grading scheme file.

    Returns:
        set: A set of variables used in the grading scheme (e.g., {USERNAME}, {U}).
    """
    return set(re.findall(r'{(\w+)}', grading_scheme_content))


def load_grading_scheme(grade_it_path, valid_variables):
    """
    Converts the answer key to YAML, loads the grading scheme, and validates its fields against the CSV headers.

    Args:
        grade_it_path (dict): GradeMaster paths containing the answer key and grading scheme file locations.
        valid_variables (list): A list of valid CSV headers representing student data.

    Returns:
        dict: A dictionary representing the validated grading scheme if successful. The program will exit otherwise.
    """
    answer_key_file = grade_it_path['answer_key_file']
    grading_scheme_file = grade_it_path['grading_scheme_file']

    # Convert answer key to YAML format
    try:
        convert_answer_key_to_yaml(answer_key_file, grading_scheme_file)
    except Exception as e:
        logging.error(f"An error occurred while converting answer key to YAML: {e}. Exiting.")
        sys.exit(1)

    # Load grading scheme from the YAML file
    try:
        with open(grading_scheme_file, 'r') as yamlfile:
            grading_scheme_content = yamlfile.read()
            grading_scheme = yaml.safe_load(grading_scheme_content)

        # Validate that all variables in the grading scheme are present in the CSV headers
        grading_scheme_variables = extract_grading_scheme_variables(grading_scheme_content)
        missing_fields = [var for var in grading_scheme_variables if var.lower() not in valid_variables]

        if missing_fields:
            logging.error(f"Validation failed: Fields referenced in the grading scheme are missing from the CSV file: {missing_fields}. Exiting.")
            sys.exit(1)

        # Validate the grading scheme structure
        if not validate_grading_scheme(grading_scheme):
            logging.error("Validation failed: Grading scheme structure is invalid. Exiting.")
            sys.exit(1)

        logging.info("Grading scheme fields successfully validated against CSV headers.")
        return grading_scheme

    except Exception as e:
        logging.error(f"An error occurred while loading the grading scheme: {e}. Exiting.")
        sys.exit(1)


def validate_grading_scheme(grading_scheme):
    """
    Validates the structure and variables of the grading scheme.

    Args:
        grading_scheme (dict): The grading scheme dictionary.

    Returns:
        bool: True if the grading scheme is valid, False otherwise.
    """
    # Check if student_data exists and contains at least one file
    if "grading_structure" not in grading_scheme or not grading_scheme["grading_structure"]:
        logging.error("Validation failed: The grading scheme must contain at least one file in 'student_data'.")
        return False

    # Iterate through each file in student_data
    for file_data in grading_scheme["grading_structure"]:
        if "filename" not in file_data or not file_data["filename"]:
            logging.error("Validation failed: Each grading scheme entry must have a 'filename'.")
            return False

        # Validate that each file has at least one task
        if "tasks" not in file_data or not file_data["tasks"]:
            logging.error(f"Validation failed: The file '{file_data['filename']}' must contain at least one task.")
            return False

        # Iterate through each task in the file
        for task in file_data["tasks"]:
            if "task" not in task or not task["task"]:
                logging.error(f"Validation failed: A task in file '{file_data['filename']}' is missing a 'task' description.")
                return False

            # Validate that each task contains at least one line
            if "lines" not in task or not task["lines"]:
                logging.error(f"Validation failed: The task '{task['task']}' in file '{file_data['filename']}' must contain at least one line.")
                return False

            # Validate that each task contains at least one line
            if "lines" not in task or not task["lines"]:
                logging.error(
                    f"Validation failed: The task '{task['task']}' in file '{file_data['filename']}' must contain at least one line.")
                return False

            # Iterate through each line in the task
            for line in task["lines"]:
                if "points" not in line:
                    logging.error(f"Validation failed: A line in task '{task['task']}' of file '{file_data['filename']}' is missing the 'points' field.")
                    return False
                if "detail" not in line:
                    logging.error(f"Validation failed: A line in task '{task['task']}' of file '{file_data['filename']}' is missing the 'detail' field.")
                    return False

    # Additional Orphaned Attribute Check for DETAIL and FEEDBACK
    for file_data in grading_scheme["grading_structure"]:
        for task in file_data["tasks"]:
            last_line = None
            for line in task.get("lines", []):
                if "line" in line:
                    last_line = line
                if "detail" in line or "feedback" in line:
                    if not last_line:
                        logging.error(f"Validation failed: Orphaned 'detail' or 'feedback' found in task '{task['task']}' of file '{file_data['filename']}'.")
                        return False

    logging.info("Grading scheme successfully validated.")
    return True


def initialize_feedback_and_results(grade_it_paths, grading_scheme):
    """
        Initializes general feedback and opens the CSV file for storing student results.

        Args:
            grade_it_paths (dict): GradeMaster paths containing necessary directories and files.

        Returns:
            tuple: A tuple containing:
                - general_feedback (dict): An initialized general feedback dictionary.
                - csv_writer (csv.DictWriter): A CSV writer object for writing student results.
                - csv_file_handle (file object): The open CSV file handle to be used for writing.
    """

    course = grading_scheme.get('course', 'Unknown Course')
    lab = grading_scheme.get('lab', 'Unknown Lab')
    professor = grading_scheme.get('professor', 'Unknown Professor')
    total_points = grading_scheme.get('total_points', 0)

    general_feedback = OrderedDict([
        ("lab", f"{course} {lab}"),
        ("graded_by", professor),
        ("total_points", total_points),
        ("total_students", 0),
        ("average_score", 0),
        ("pass_rate", 0),
        ("passing_students", 0),
        ("tasks", [])
    ])

    # Open the CSV file in write mode (will overwrite if it already exists)
    csv_file = grade_it_paths['grades_csv_file']
    csv_file_handle = open(csv_file, 'w', newline='')

    # Define the fieldnames for the CSV
    fieldnames = ['username', 'earned_points']

    # Initialize CSV DictWriter
    csv_writer = csv.DictWriter(csv_file_handle, fieldnames=fieldnames)

    # Write header to the file
    csv_writer.writeheader()

    return general_feedback, csv_writer, csv_file_handle


def save_all_feedback(graded_students, general_feedback, csv_file_handle, grade_it_paths):
    """
    Saves all student feedback, general feedback, and final grades after grading is done.

    Args:
        graded_students (list): A list of dictionaries with graded student feedback.
        general_feedback (dict): The general feedback to be saved.
        csv_file_handle (file object): The open CSV file handle to be closed.
        grade_it_paths (dict): GradeMaster paths containing necessary directories and files.
    """
    # Close the CSV file after grading is complete
    csv_file_handle.close()

    # Add all student feedback to the general feedback
    general_feedback['feedback'].extend(graded_students)

    # Save general feedback to a file
    feedback_file_path = grade_it_paths['general_feedback_file']
    with open(feedback_file_path, 'w') as file:
        yaml.dump(general_feedback, file, default_flow_style=False, allow_unicode=True)

    logging.info("All feedback has been saved successfully.")


def grade_students_submission(students, paths, grading_scheme, general_feedback, csv_writer):
    """
    Processes each student's submission, evaluates it, and updates feedback structures.

    Args:
        students (list): List of dictionaries containing student information.
        paths (dict): Paths to relevant files and directories for grading.
        grading_scheme (dict): The grading scheme dictionary.
        general_feedback (dict): General feedback to be saved for all students.
        csv_writer (csv.DictWriter): CSV writer object to write student grades to the grades.csv file.
    """

    # Get the grading_scheme -- grading_structure
    grading_structure = grading_scheme["grading_structure"]

    # Handles all students
    for student in students:

        # Iterate over a student
        username = student['username']

        total_results = {
            "total_points": 0.0,
            "earned_points": 0.0,
            "feedback": []
        }

        # Iterate over all files in grading_structure
        for file_data in grading_structure:

            # Filename in the grading_structure
            file_name = file_data["filename"]
            tasks = file_data["tasks"]

            # Read the student file data
            student_file_data = read_student_files(username, file_name, paths['submissions_dir'])

            # Evaluate the student's tasks in a file if data is not None
            if student_file_data is None:
                logging.info(f"No submission or empty submission for student {username} in file '{file_name}'")
                continue  # Skip to the next file if no valid results for the current file

            # Evaluate the student's tasks in a file
            file_results = evaluate_student_data(student, student_file_data, tasks)

            if file_results is None:
                logging.info(f"No submission or empty submission for student {username} in file '{file_name}'")
                continue # Skip to the next file if no valid results for the current file

            # Accumulate points and feedback from file_results
            total_results["total_points"] += file_results.get("total_points", 0)
            total_results["earned_points"] += file_results.get("earned_points", 0)
            total_results["feedback"].extend(file_results.get("feedback", []))

        # Save  student feedback
        save_student_feedback(student, total_results, grading_scheme, paths['feedback_dir'])
        # update_general_feedback(general_feedback, total_results, grading_scheme)

        # Write student results to the open CSV file using DictWriter
        earned_points = 0 if total_results is None else total_results.get('earned_points', 0)

        # Prepare the dictionary to be written
        student_result = {
            'username': username,
            'earned_points': earned_points
        }
        csv_writer.writerow(student_result)

        logging.debug(f"Results saved for {username}")


def finalize_feedback_and_close_csv(general_feedback, csv_file_handle, grade_it_paths):
    """
        Finalizes feedback by saving general feedback and closing the CSV file used for grading results.

        Args:
            general_feedback (dict): The general feedback to be saved.
            csv_file_handle (file object): The open CSV file handle to be closed.
            grade_it_paths (dict): GradeMaster paths containing necessary directories and files.
    """
    csv_file_handle.close()
    logging.debug("grades.csv file closed successfully.")

    general_feedback_file = grade_it_paths['general_feedback_file']
    with open(general_feedback_file, 'w') as yamlfile:
        yaml.dump(general_feedback, yamlfile, default_flow_style=False, allow_unicode=True)

    logging.debug("General feedback has been saved successfully.")


def create_or_load_config(config_path="./config.yaml"):
    """
    Loads the configuration from a YAML file, or prompts the user to create a new one if not provided.
    Validates the directories and files to ensure everything is set up correctly.

    Args:
        config_path (str): Path to the config file.

    Returns:
        dict: A valid configuration dictionary if successful. Exits on failure.
    """
    try:
        if os.path.exists(config_path):
            logging.info(f"Loading configuration from {config_path}")
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
        else:
            logging.warning("Configuration file not found. Let's create a new one.")
            config = prompt_user_for_config()

        # Validate directories and files after loading or creating configuration
        if not validate_directories_and_files(config):
            logging.error("Directory or file validation failed. Exiting.")
            sys.exit(1)

    except Exception as e:
        logging.error(f"An error occurred while loading or creating the configuration: {e}. Exiting.")
        sys.exit(1)

    return config


def prompt_user_for_config():
    """Prompt the user for paths and create a new configuration file."""
    def get_validated_path(prompt_message):
        while True:
            path = input(prompt_message).strip().strip('"')
            if os.path.isabs(path) and os.path.exists(path):
                logging.info(f"Valid path provided: {path}")
                return path
            else:
                logging.error("Invalid path. Please provide an absolute path in quotation marks.")

    student_list_path = get_validated_path('Provide the full path to CSV file with your student list: ')
    submissions_dir = get_validated_path('Provide the full path to the directory containing files that you wish to grade: ')
    answer_file_path = get_validated_path('Provide the full path to your answer file: ')

    results_dir = os.path.join(submissions_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    logging.info(f"Created results directory at: {results_dir}")

    config = {
        'students_file': student_list_path,
        'submissions_dir': submissions_dir,
        'answer_key_file': answer_file_path,
        'results_dir': results_dir,
        'feedback_dir': os.path.join(results_dir, "feedback"),
        'general_feedback_file': os.path.join(results_dir, "general_feedback.yaml"),
        'grading_scheme_file': os.path.join(results_dir, "grading_scheme.yaml"),
        'grades_csv_file': os.path.join(results_dir, "grades.csv")
    }

    return config


def parse_arguments():
    parser = argparse.ArgumentParser(description='GradeIt: Flexible grading tool based on an answer key.')
    parser.add_argument('--config', type=str, help='Path to the config.yaml file', default="./config.yaml")
    return parser.parse_args()


def main():
    """
    Function to execute the grading workflow

    1. Parse arguments
    2. Setup logging & YAML
    3. Load configuration and validate paths from config.yaml (specified path or user input)
    4. Load students and valid variables to use in the grading headers
    5. Load and validate grading scheme
    6. Initialize general feedback and open CSV file for student results
    8. Grade students submission
    9. Save feedback and grades after grading all students
    """

    args = parse_arguments()
    configure_globals()
    grade_it_paths = create_or_load_config(args.config)
    students, valid_variables = load_students(grade_it_paths)
    grading_scheme = load_grading_scheme(grade_it_paths, valid_variables)
    general_feedback, csv_writer, cvs_file_handler = initialize_feedback_and_results(grade_it_paths, grading_scheme)
    grade_students_submission(students, grade_it_paths, grading_scheme, general_feedback, csv_writer)
    finalize_feedback_and_close_csv(general_feedback, cvs_file_handler, grade_it_paths)


if __name__ == "__main__":
    main()

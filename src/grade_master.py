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


SPECIAL_CHAR = "#"


def parse_special_line(line):
    """
    Parses a line to extract points or keyword-value pairs.

    Args:
        line (str): The line to parse.

    Returns:
        tuple: A tuple containing points and value, or keyword and value.
    """
    match = re.match(r"^#\[\s*(\d+)\s*\](.*)", line)
    if match:
        points = int(match.group(1).strip())
        value = match.group(2).strip()
        return points, value
    else:
        match = re.match(r"^#\[\s*(\w+)\s*:\s*(.*?)\s*\]", line)
        if match:
            keyword = match.group(1).strip()
            value = match.group(2).strip()
            return keyword, value
    return None, None

def convert_answer_key_to_yaml(answer_key_path, output_path):
    """
    Converts an answer key file to a YAML grading scheme.

    Args:
        answer_key_path (str): The path to the answer key file.
        output_path (str): The path to the output YAML file.
    """

    grading_scheme = {
        "course": "NONE",
        "lab": "NONE",
        "professor": "NONE",
        "files": "NONE",
        "tasks": []
    }
    current_task = None

    try:
        with open(answer_key_path, 'r') as file:
            # Read the first few lines for course, lab, professor, and files
            for _ in range(4):
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

            logging.debug(f"Initial course, lab, professor: {grading_scheme}")

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
                        current_task = {"task": value, "lines": []}
                    elif keyword == "DETAIL":
                        if current_task and current_task["lines"]:
                            current_task["lines"][-1]["detail"] = value
                    elif keyword == "FEEDBACK":
                        if current_task and current_task["lines"]:
                            current_task["lines"][-1]["feedback"] = value
                    else:
                        try:
                            points = int(keyword)
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

    Args:
        username (str): The username of the student.
        file_name (str): The name of the file to read.
        data_directory (str): The directory where student files are located.

    Returns:
        str: The contents of the student's file.
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

    Args:
        students_file (str): The path to the students CSV file.

    Returns:
        list: A list of dictionaries with 'username' and 'uid'.
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
    #return re.search(answer_key_line, student_line) is not None

    # Adjust the pattern to handle spaces and optionally trailing characters
    #answer_key_line = re.escape(answer_key_line).replace(r'\ ', r'\\s*') + '.*'

    # Adjust the pattern to handle spaces
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


def preprocess_answer_key_for_student(answer_key, uid):
    """
    Replaces '{U}' in the answer key with the student's UID.

    Args:
        answer_key (str): The answer key line.
        uid (str): The student's unique ID.

    Returns:
        str: The preprocessed answer key line.
    """
    if uid is not None:
        return answer_key.replace('{U}', str(uid)).strip()
    return answer_key.strip()

def evaluate_student_data(student_data, grading_scheme, uid):
    """
    Evaluates the student's data against the grading scheme.

    Args:
        student_data (str): The student's data.
        grading_scheme (dict): The grading scheme containing tasks and lines to match.

    Returns:
        dict: The evaluation results, including total points and feedback.
    """

    if not student_data.strip():
        return None

    results = {
        "total_points": 0,
        "earned_points": 0,
        "feedback": []
    }

    for task in grading_scheme["tasks"]:
        task_feedback = {
            "task": task["task"],
            "points": 0,
            "earned": 0,
            "details": [],
            "feedback": []
        }

        for line in task["lines"]:
            answer_key_line = preprocess_answer_key_for_student(line["line"], uid)
            points = line["points"]
            detail = line.get("detail", "")
            feedback = line.get("feedback", "")

            results["total_points"] += points
            task_feedback["points"] += points

            if any(match_line(student_line, answer_key_line) for student_line in student_data.splitlines()):
                task_feedback["earned"] += points
                results["earned_points"] += points
                task_feedback["details"].append(detail)
            else:
                task_feedback["feedback"].append(feedback)

        results["feedback"].append(task_feedback)

    return results


from tabulate import tabulate

def save_student_feedback(student, results, grading_scheme, output_dir):
    """
    Saves feedback for the student in a text file using the tabulate package.

    Args:
        results (dict): The evaluation results.
        grading_scheme (dict): The grading scheme.
        student (dict): A dictionary with 'username' and 'uid'.
        output_dir (str): The directory where the feedback file should be saved.
    """
    # Extract course, lab, and professor information from the grading scheme
    course = grading_scheme.get('course', 'Unknown Course')
    lab = grading_scheme.get('lab', 'Unknown Lab')
    professor = grading_scheme.get('professor', 'Unknown Professor')
    student_uid = student.get('uid', None)

    # Create the feedback file path
    feedback_file = os.path.join(output_dir, f"{student['username']}-feedback.txt")

    # Write the feedback to the file
    with open(feedback_file, 'w') as file:
        # Write the header
        file.write(f"{course} - {lab}\n")
        file.write(f"+{'-' * 68}+\n")
        file.write(f"|  Marked on {datetime.now().strftime('%a %d %b %Y %H:%M:%S %z')}\n")
        file.write(f"|  Marked by {professor}\n")
        file.write(f"|  Student ID {student['username']}\n")
        file.write(f"+{'-' * 68}+\n\n")

        if results is None:
            file.write("No submission or empty submission\n")
            logging.info(f"No submission or empty submission for student {student['username']}")
            return

        headers = ["Task", "Detail/Feedback", "Earned", "Points"]
        table = []

        # Add logging to debug the structure of the results
        logging.debug(f"Results structure: {results}")

        for task_result in results['feedback']:
            task_name = task_result.get('task', 'Unknown Task')
            details = task_result.get('details', [])
            feedbacks = task_result.get('feedback', [])
            points = task_result.get('points', 0)
            earned = task_result.get('earned', 0)

            # Add task row
            table.append([task_name, "", earned, points])

            # Ensure details and feedbacks are handled correctly
            for detail in details:
                # Replace {U} with the student's UID in details and feedbacks if UID is not NONE
                if student['uid'] and student['uid'] != 'NONE':
                    detail = detail.replace("{U}", student['uid'].strip())
                row = ["", detail, "", ""]
                table.append(row)

            for feedback in feedbacks:
                if student['uid'] and student['uid'] != 'NONE':
                    feedback = feedback.replace("{U}", student['uid'].strip())
                row = ["", feedback, "", ""]
                table.append(row)

            table.append(["", "", "", ""])


        # Add a separator line and total and earned points at the end
        table.append(["", "", "", ""])
        total_points = results.get('total_points', 0)
        earned_points = results.get('earned_points', 0)
        table.append(["Total Points", "", earned_points, total_points])

        # Write the table to the file with column alignment
        file.write(tabulate(table, headers=headers, tablefmt="pretty", colalign=("left", "left", "center", "center")))

    logging.debug(f"Feedback saved to {feedback_file}")

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
        #writer.writerow([f'#{student['username']}, {results['earned_points']}#'])

    logging.debug(f"Results saved to {csv_file}")


def parse_arguments():
    parser = argparse.ArgumentParser(description='GradeMaster: A flexible grading tool based on an answer key.')
    parser.add_argument('root_dir', type=str, help='The root directory for the course.')
    parser.add_argument('lab', type=str, help='The lab number or name.')
    return parser.parse_args()


def main():
    """
    Main function to run the GradeMaster script.
    Parses arguments, validates directories and files, converts the answer key to a YAML grading scheme, loads students, evaluates their data, and saves feedback.
    """

    # Parse arguments
    args = parse_arguments()

    root_dir = args.root_dir
    lab_name = args.lab

    # Set up logging
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

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

    for student in students:
        username = student['username']
        uid = student['uid']
        student_data = read_student_files(username, file_name, submissions_dir)

        # Evaluate the student's data
        results = evaluate_student_data(student_data, grading_scheme, uid)
        # Log the results for now, you can save it to a file or database as needed

        # Save feedback for the student
        save_student_feedback(student, results, grading_scheme, feedback_dir)

        logging.debug(f"Results for student {username}: {results}")

        if results is not None:
            logging.debug(f"Results for student {username}: {results}")
            save_student_results_to_csv(student, results, lab_name, lab_dir)
        else:
            save_student_results_to_csv(student, {"earned_points": 0}, lab_name, lab_dir)

        logging.debug(f"Results for student {username}: {results}")

if __name__ == "__main__":
    main()

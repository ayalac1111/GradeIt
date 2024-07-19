#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        logging.debug(f"Match found: {match.group(0)}")
    else:
        logging.debug("No match found")

    return match is not None

def evaluate_student_data(student_data, grading_scheme):
    """
    Evaluates the student's data against the grading scheme.

    Args:
        student_data (str): The student's data.
        grading_scheme (dict): The grading scheme containing tasks and lines to match.

    Returns:
        dict: The evaluation results, including total points and feedback.
    """
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
            answer_key_line = line["line"]
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

def save_feedback(student, feedback, total_points, earned_points, lab_info, data_directory):
    """
    Saves feedback for the student in a Markdown file.

    Args:
        student (dict): A dictionary with 'username' and 'uid'.
        feedback (list): A list of feedback messages.
        total_points (int): The total points possible.
        earned_points (int): The points earned by the student.
        lab_info (dict): A dictionary with lab information.
        data_directory (str): The path to the data directory.
    """

    feedback_file = os.path.join(data_directory, f"{student['username']}_feedback.md")

    with open(feedback_file, 'w') as file:
        # Write the header
        file.write(f"{lab_info['course']} - {lab_info['lab']}\n\n")
        file.write("---")
        file.write(f"Marked on {datetime.now().strftime('%a %d %b %Y %H:%M:%S %Z')}\n")
        file.write(f"Marked by  {lab_info['professor']}\n")
        file.write(f"Student ID {student['username']}\n")
        file.write("---\n\n")

        logging.info(f"Feedback structure: {feedback}")

        # Write the feedback for each task
        task_number = 1
        for task_feedback in feedback:
            file.write(f"TASK {task_number} - {task_feedback['task']}\n\n")
            task_number += 1

            # Write the table header
            file.write("| Detail | Points | Earned |\n")
            file.write("|--------|--------|--------|\n")

            for i, detail in enumerate(task_feedback['details']):
                points = task_feedback['points']
                earned = task_feedback['earned']
                file.write(f"| {detail} | {points} | {earned} |\n")

                # Write the feedback if points are not earned
                if earned == 0:
                    feedback_message = task_feedback['feedback']
                    file.write(f"FEEDBACK: {feedback_message}\n")

            file.write("---\n\n")

        # Write the final information
        file.write("## DISPLAYING FINAL INFORMATION\n\n")
        file.write(f"{lab_info['course']} - {lab_info['lab']}: {earned_points}\n")
        file.write(f"{lab_info['course']} - {lab_info['lab']} GRADE: {earned_points} / {total_points}\n\n")
        file.write("---\n\n")

        # List submitted files
        file.write("## Students Files:\n\n")
        files = os.listdir(data_directory)
        for f in files:
            if student['username'] in f:
                file.write(f"- {f}\n")

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

    # Create the feedback file path
    feedback_file = os.path.join(output_dir, f"{student['username']}_feedback.txt")

    # Write the feedback to the file
    with open(feedback_file, 'w') as file:
        # Write the header
        file.write(f"{course} - {lab}\n")
        file.write(f"+{'-' * 68}+\n")
        file.write(f"|  Marked on {datetime.now().strftime('%a %d %b %Y %H:%M:%S %z')}\n")
        file.write(f"|  Marked by {professor}\n")
        file.write(f"|  Student ID {student['username']}\n")
        file.write(f"+{'-' * 68}+\n\n")

        headers = ["Task", "Detail/Feedback", "Points", "Earned"]
        table = []

        # Add logging to debug the structure of the results
        logging.debug(f"Results structure: {results}")

        for task_result in results['feedback']:
            task_name = task_result.get('task', 'Unknown Task')
            details = task_result.get('details', [])
            feedbacks = task_result.get('feedback', [])
            points = task_result.get('points', 0)
            earned = task_result.get('earned', 0)

            # Ensure details and feedbacks are handled correctly
            max_len = max(len(details), len(feedbacks))
            for i in range(max_len):
                detail = details[i] if i < len(details) else ''
                feedback = feedbacks[i] if i < len(feedbacks) else ''
                feedback_display = feedback if earned < points else ''  # Only show feedback when earned is less than points

                if detail == '':
                    detail = feedback_display

                row = [
                    task_name if i == 0 else '',  # Only show the task name once
                    detail,
                    points if i == 0 else '',  # Only show points once per task
                    earned if i == 0 else '',  # Only show earned points once per task
                    #feedback_display
                ]
                table.append(row)
                task_name = ''  # Only show the task name once

            table.append(["", "", "", ""])


        # Add a separator line and total and earned points at the end
        table.append(["", "", "", ""])
        total_points = results.get('total_points', 0)
        earned_points = results.get('earned_points', 0)
        table.append(["Total Points", "", total_points, earned_points])

        #print(f"\nStudent ID {student['username']}\n")
        #print(tabulate(table, headers=headers, tablefmt="pretty"))
        # Write the table to the file
        file.write(tabulate(table, headers=headers, tablefmt="pretty"))

    logging.info(f"Feedback saved to {feedback_file}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='GradeMaster: A flexible grading tool based on an answer key.')
    parser.add_argument('key_dir', type=str, help='The directory where the answer_key and grading_scheme are located.')
    parser.add_argument('data_dir', type=str, help='The directory where the students data is located.')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    key_dir = args.key_dir
    data_dir = args.data_dir

    # Validate key_dir
    if not os.path.isdir(key_dir):
        logging.error(f"The key directory '{key_dir}' does not exist.")
        sys.exit(1)

    # Validate required files in key_dir
    required_files = ['answer_key.txt', 'students.csv']
    for required_file in required_files:
        file_path = os.path.join(key_dir, required_file)
        if not os.path.isfile(file_path):
            logging.error(f"Required file '{required_file}' not found in the key directory '{key_dir}'.")
            sys.exit(1)

    # Validate data_dir
    if not os.path.isdir(data_dir):
        logging.error(f"The data directory '{data_dir}' does not exist.")
        sys.exit(1)

    logging.info(f"All required files are present in '{key_dir}' and '{data_dir}' directories.")

    # Convert answer_key.txt to grading_scheme.yaml
    answer_key_path = os.path.join(key_dir, 'answer_key.txt')
    output_path = os.path.join(key_dir, 'grading_scheme.yaml')
    convert_answer_key_to_yaml(answer_key_path, output_path)

    # Load grading scheme
    with open(output_path, 'r') as yamlfile:
        grading_scheme = yaml.safe_load(yamlfile)

    # Load students
    students_file = os.path.join(key_dir, 'students.csv')
    students = load_students(students_file)

    # Read and process student files
    file_name = grading_scheme.get("files")
    if file_name == "NONE":
        logging.error("No FILES keyword found in the answer_key.")
        sys.exit(1)

    for student in students:
        username = student['username']
        student_data = read_student_files(username, file_name, data_dir)

        # Evaluate the student's data
        results = evaluate_student_data(student_data, grading_scheme)
        # Log the results for now, you can save it to a file or database as needed

         # Save feedback for the student
        save_student_feedback( student, results, grading_scheme, data_dir )

        logging.info(f"Results for student {username}: {results}")

if __name__ == "__main__":
    main()

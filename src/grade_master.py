#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys
import re
import yaml


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
    result = {
        "course": "NONE",
        "lab": "NONE",
        "professor": "NONE",
        "files": "NONE",
        "tasks": []
    }
    tasks = []
    current_task = None

    try:
        with open(answer_key_path, 'r') as file:
            # Read the first three lines for course, lab, and professor
            for _ in range(4):
                line = file.readline()
                if not line:
                    break
                keyword, value = parse_special_line(line)
                if keyword == "COURSE":
                    result["course"] = value
                elif keyword == "LAB":
                    result["lab"] = value
                elif keyword == "PROFESSOR":
                    result["professor"] = value
                elif keyword == "FILES":
                    result["files"] = value

            logging.debug(f"Initial course, lab, professor: {result}")

            # Process the remaining lines for tasks
            for line in file:
                logging.debug(f"Processing line: {line.strip()}")
                keyword, value = parse_special_line(line)
                if keyword:
                    logging.debug(f"Found keyword: {keyword}, value: {value}")
                    if keyword == "TASK":
                        if current_task and current_task["lines"]:
                            logging.debug(f"----CURRENT: {current_task}")
                            tasks.append(current_task)
                        current_task = {"task": value, "lines": []}
                        logging.debug(f"----TASK: {current_task}")
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
                            logging.warning(f"Unknown keyword or invalid points '{keyword}' in line: {line.strip()}")

            if current_task and current_task["lines"]:
                logging.debug(f"appending: {current_task}")
                tasks.append(current_task)

        result["tasks"] = tasks
        logging.debug(f"Final result: {result}")

        with open(output_path, 'w') as yamlfile:
            yaml.dump(result, yamlfile, default_flow_style=False)

        logging.info(f"Successfully converted {answer_key_path} to {output_path}")

    except FileNotFoundError:
        logging.error(f"File not found: {answer_key_path}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

import os
import csv
import logging

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
    return re.search(answer_key_line, student_line) is not None

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



def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='GradeMaster: A flexible grading tool based on an answer key.')
    parser.add_argument('key_dir', type=str, help='The directory where the answer_key and grading_scheme are located.')
    parser.add_argument('data_dir', type=str, help='The directory where the students data is located.')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.info(f"Results for student {username}: {results}")

if __name__ == "__main__":
    main()

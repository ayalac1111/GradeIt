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
        "tasks": []
    }
    tasks = []
    current_task = None

    try:
        with open(answer_key_path, 'r') as file:
            # Read the first three lines for course, lab, and professor
            for _ in range(3):
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



def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='GradeMaster: A flexible grading tool based on an answer key.')
    parser.add_argument('key_dir', type=str, help='The directory where the answer_key and grading_scheme are located.')
    parser.add_argument('data_dir', type=str, help='The directory where the students data is located.')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

if __name__ == "__main__":
    main()

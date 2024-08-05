# GradeMaster

GradeMaster is a flexible and automated grading tool designed to evaluate student submissions against an answer key using regular expressions. This tool is built to handle various types of assignments and provide detailed feedback for students.

## Features

- **Flexible Answer Key**: Uses regular expressions to match student submissions.
- **Variable Handling**: Supports unique identifiers (UID) for personalized grading.
- **Detailed Feedback**: Generates detailed feedback files for each student.
- **CSV Reporting**: Outputs a CSV file with the grading results for all students.
- **Markdown and Text Feedback**: Saves feedback in a readable format using `tabulate`.

## Getting Started

### Prerequisites

- Python 3.x
- Required Python packages: `argparse`, `logging`, `os`, `sys`, `re`, `yaml`, `datetime`, `csv`, `tabulate`

Install the required packages using pip:

```sh
pip install pyyaml tabulate
```

### Repository Structure

```shell
GradeMaster/

├── FEATURES.md
├── LICENE
├── README.md
├── requirements.txt
├── src
│   ├── __init__.py
│   └── grade_master.py
└── tests
    └── __init__.py
```

### Directory Structure

To organize your course and lab data, use the following directory structure:

```bash
24S-CST8371
├── students.csv
├── Labs
    ├── 11
    │   ├── 11-grades.csv
    │   ├── 11_answer_key.txt**
    │   ├── 11_grading_scheme.yaml
    │   ├── feedback
    │   │   ├── abcd0001-feedback.txt
    │   │   ├── abcd0002-feedback.txt
    │   │   └── abcd0003-feedback.txt
    │   └── submissions
    │   │   ├── abcd0001-11.txt
    │   │   ├── abcd0002-11.txt
    │   │   └── abcd0003-11.txt
    ├── 12
        ├── 12-grades.csv
        ├── 12_answer_key.txt**
        ├── 12_grading_scheme.yaml
        ├── feedback
        │   ├── abcd0001-feedback.txt
        │   ├── abcd0002-feedback.txt
        │   └── abcd0003-feedback.txt
        └── submissions
            ├── abcd0001-11.txt
            ├── abcd0002-11.txt
            └── abcd0003-11.txt

```

### Usage

To use GradeMaster, run the `grade_master.py` script with the root directory and lab number/name as arguments.

### Command Line


``` bash
python grade_master.py <root_directory> <lab_number_or_name>
```

- `<root_directory>`: The root directory for the course (e.g., `24S-CST8371`).
- `<lab_number_or_name>`: The lab number or name (e.g., `10` or `NAT`).

### Example


``` bash
python grade_master.py 24S-CST8371 10
```

This will:

1. Load the students from `24S-CST8371/students.csv`.
2. Read the answer key from `24S-CST8371/Labs/10/10_answer_key.txt`.
3. Convert the answer key to `24S-CST8371/Labs/10/10_grading_scheme.yaml`.
4. Read student submissions from `24S-CST8371/Labs/10/submissions/`.
5. Evaluate each student's submission and save feedback in `24S-CST8371/Labs/10/feedback/`.
6. Save the grades to `24S-CST8371/Labs/10/10_grades.csv`.

## Features

- Flexible grading based on a customizable answer key.
- Supports multiple labs and organizes data efficiently.
- Generates feedback for each student and saves it in a structured format.
- Saves grades to a CSV file for easy access and review.

## Requirements

Make sure to have the necessary Python packages installed:

```bash
pip install -r requirements.txt
```

### Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

### License

This project is licensed under the MIT License. See the LICENSE file for details.

### Contact

For any questions or suggestions, please contact Carolina Ayala.


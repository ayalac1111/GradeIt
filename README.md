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
├── TestData
│   ├── Data
│   │   ├── abcd0001-data.txt
│   │   ├── abcd0002-data.txt
│   │   ├── abcd0003-data.txt
│   │   └── abcd0004-data.txt
│   └── Keys
│       ├── answer_key.txt
│       └── students.csv
├── requirements.txt
├── src
│   ├── __init__.py
│   └── grade_master.py
└── tests
    └── __init__.py
```

### Usage

1. **Prepare the Answer Key**: Create an `answer_key.txt` file in the key directory with tasks and expected outputs using special characters for regular expressions and variables.
    
2. **Prepare Student Data**: Place student submission files in the data directory. Ensure the `students.csv` file is present in the key directory with the format `username, uid`.
    
3. **Run GradeMaster**: Execute the `grade_master.py` script with the key and data directories as arguments

**students.csv**:

```csv
abcd0001, 101
abcd0002, 102
```

4. **Review Results**: The results will be saved in the data directory as `<username>_feedback.txt` and a summary CSV file will be generated as `<labname>-grades.csv`.

### Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

### License

This project is licensed under the MIT License. See the LICENSE file for details.

### Contact

For any questions or suggestions, please contact Carolina Ayala.


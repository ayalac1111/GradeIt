# GradeIt

**GradeIt** is a flexible and automated grading tool designed to evaluate student submissions against an answer key using regular expressions. This tool is built to handle various types of assignments and provide detailed feedback for students.

## Features

- **Flexible Answer Key**: Uses regular expressions to match student submissions.
- **Variable Handling**: Supports unique identifiers (UID) for personalized grading.
- **Detailed Feedback**: Generates detailed feedback files for each student.
- **CSV Reporting**: Outputs a CSV file with the grading results for all students.
- **Text Feedback**: Saves feedback in a readable format using `tabulate`.
- **General feedback**:  Aggregates general feedback to track overall student performance.

## Getting Started

#### Requirements

Make sure to have the necessary Python packages installed:

```bash
pip install -r requirements.txt
```

### Usage

To use GradeIt, you need a `config.yaml` file to specify the paths and filenames for submissions, feedback, answer key, etc.

### Command Line

You can run the script with the following command:

``` bash
python grade_it.py --config ./config.yaml
```

Alternatively, you can run the script without arguments, and it will default to using a `config.yaml` file in the current directory:

#### Configuration File (`config.yaml`)

The `config.yaml` file contains the paths and filenames for grading. Below is an example structure:

``` yaml
submissions_dir: /path/to/submissions 
feedback_dir: /path/to/feedback 
general_feedback_file: /path/to/general_feedback.yaml 
answer_key_file: /path/to/answer_key.txt 
grading_scheme_file: /path/to/grading_scheme.yaml 
students_file: /path/to/students.csv 
grades_csv_file: /path/to/grades.csv`
```


### Example

Assuming the following `config.yaml`:

``` yaml
submissions_dir: ./NET3008/Labs/OSPF/submissions
feedback_dir: ./NET3008/Labs/OSPF/feedback
general_feedback_file: ./NET3008/Labs/OSPF/general_feedback.yaml
answer_key_file: ./NET3008/Labs/OSPF/OSPF_answer_key.txt
grading_scheme_file: ./NET3008/Labs/OSPF/OSPF_grading_scheme.yaml
students_file: ./NET3008/students.csv
grades_csv_file: ./NET3008/Labs/OSPF/OSPF_grades.csv
```

Run the script as follows:

``` bash
python grade_it.py --config ./config.yaml

```

This will:

1. Load student information from `students.csv`.
2. Read the answer key from `answer_key.txt`.
3. Process student submissions located in `submissions_dir`.
4. Generate feedback in `feedback_dir`.
5. Save general feedback to `general_feedback_file`.
6. Output grades to `grades_csv_file`.

### Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

### License

This project is licensed under the MIT License. See the LICENSE file for details.

### Contact

For any questions or suggestions, please contact Carolina Ayala.




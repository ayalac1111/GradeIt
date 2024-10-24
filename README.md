# GradeIt

**GradeIt** is a Python-based automation tool designed for consistent evaluation of student submissions, generating timely feedback for networking courses. It allows instructors to grade student submissions in a consistent and automated manner, supporting grading across multiple files and task types. The script leverages YAML for configuration, providing flexibility and clear instructions for grading criteria. This tool is built to handle various types of assignments and provide detailed feedback for students.

---
## Features

- **Multi-file Grading**: Supports grading submissions across multiple files, as defined by the grading scheme.
- **Flexible Grading Structure**: The grading scheme is defined using a text answer key converted into a YAML file, allowing for easy configuration of tasks, point allocation, and evaluation logic.
- **Multiple Variable Handling**: Supports unique variables for each student, such as IP addresses, VLANs, and lab sections, making grading more personalized.
- **Detailed Feedback**: Generates a detailed feedback report for each student, including feedback for each task.
- **Customizable Feedback Options**: Allows instructors to decide which information is provided as feedback to students.
- **General and Individual Feedback Management**: Generates and maintains feedback for each student, as well as general course-level feedback.
- **CSV Grade Output**: Writes students' grades to a `grades.csv` file for easy import into learning management systems (LMS).
- **Variable Handling**: Supports unique identifiers (UID) for personalized grading.

---

## How It Works

1. **Configuration and Setup**: The script reads a configuration file (`config.yaml`) which defines various paths and parameters required for grading.
2. **Answer Key Conversion**: The provided answer key file is parsed and converted to a YAML grading scheme, which includes the course name, lab name, tasks, and the associated grading points.
3. **Student Data Loading**: A CSV file with student details is loaded. This includes information such as usernames, UIDs, and other data necessary for grading.
4. **File Reading and Evaluation**: The script reads each student's submission file(s) and evaluates the content against the tasks defined in the grading scheme.
5. **Grading Logic**: For each student, the script iterates through the specified files and tasks, evaluates if the student's submission matches the criteria, and assigns points accordingly.
6. **Feedback Generation**: Detailed feedback for each student is generated and saved as a YAML file. This feedback includes which tasks were completed correctly and which ones need improvement.
7. **CSV Grade Export**: After processing all students, their grades are exported to a `grades.csv` file, containing each student's total earned points.

---
## Usage Instructions

### Dependencies:

Make sure **Python 3** is installed along with the required libraries (`PyYAML` and others). To install dependencies, run:

```bash
pip install -r requirements.txt
```

### Configuration File

To use GradeIt, you need to at least specify where the submission files are, where is the list of students to evaluate and where is the answer_key to be used to do the grading.

This information can be given at the command line:

``` bash
ayalac@huitaca:/24F-NET3008/Labs/RDIST$ grade_it.py 
Provide the full path to CSV file with your student list: 
/24F-NET3008/students.csv                     
Provide the full path to the directory containing files that you wish to grade: /24F-NET3008/submissions
Provide the full path to your answer file: /24F-NET3008/RDIST_answer_key.txt
```

As an alternative, you can use a `config.yaml` file with all the paths and filenames for grading. Below is an example structure:

``` yaml
submissions_dir: /path/to/submissions 
feedback_dir: /path/to/feedback 
general_feedback_file: /path/to/general_feedback.yaml 
answer_key_file: /path/to/answer_key.txt 
grading_scheme_file: /path/to/grading_scheme.yaml 
students_file: /path/to/students.csv 
grades_csv_file: /path/to/grades.csv`
```

Or you can use the ```--config``` option to use a different name for your config file.
### Command Line

You can run the script with the following command:

1.  When use with a config file in the current directory:
``` bash
python grade_it.py
```

Alternatively, you can run the script without a config file and answer the questions on where the main files are located.
#### Example

Assuming the following `OSPF_config.yaml`:

``` yaml
submissions_dir: ./OSPF/submissions
feedback_dir: ./OSPF/feedback
general_feedback_file: ./OSPF/general_feedback.yaml
answer_key_file: ./OSPF/OSPF_answer_key.txt
grading_scheme_file: ./OSPF/OSPF_grading_scheme.yaml
students_file: ./NET3008/students.csv
grades_csv_file: ./OSPF/OSPF_grades.csv
```

Run the script as follows:

``` bash
python grade_it.py --config ./OSPF_config.yaml

```

This will:

1. Load student information from `students.csv`.
2. Read the answer key from `answer_key.txt`.
3. Process student submissions located in `submissions_dir`.
4. Generate feedback in `feedback_dir`.
5. Save general feedback to `general_feedback_file`.
6. Output grades to `grades_csv_file`.

### **Feedback and Grading**: 
The script will generate individual feedback files for each student in the designated directory, and the overall grades will be written to `grades.csv`.

#### Example of a feedback file:

``` yaml
course:
  - course_name: 24F-NET3008
  - professor: Carolina Ayala

lab:
  - lab_name: RDIST
  - graded_on: 'Thu 24 Oct 2024 09:09:31 '
  - earned_points: 7.0
  - total_points: 10.0
  - lab_grade: 70.0%

student:
  u: '156'
  username: std0001

feedback:
  - task: (1.5 Points ) Filter Redistributed Routes Using a Distribute List and ACL
    results:
      - (0.5) R2 - Configured an ACL OSPF20-FILTER
      - (0.5) R2 - Filtered out 192.168.20.0/22 from Redistribution
      - (0) INCORRECT Ensure R2 - Red. OSPF 156 into EIGRP 156 filtered by OSPF2-FILTER
  - task: ( 4.5 Points ) Filter Red. Routes Using a Distribute List and Prefix List
    results:
      - (0.5) R2 - Configured the prefix list EIGRP-FILTER
      - (0) INCORRECT Ensure R2 - Permits 172.16.0.0/16 eq 28 from Redistribution
      - (0.5) R2 - Red. EIGRP 156 into OSPF 156 filtered by EIGRP-FILTER
      - (1) R2 - Learned 172.16.1.0/24 via OSPF as a E2 route
      - (1) R2 - Learned 172.16.12.0/26 via OSPF as a E2 route
      - (0) INCORRECT Ensure R2 - Learns 172.16.14.0/28 via OSPF as a E2 route
  - task: (2 Points ) Filter Redistributed Routes Using a Route Map
    results:
      - (0.5) R2 - Configured an ACL R3-ACL
      - (0.5) R2 - Filtered out 192.168.34.0/28 from Redistribution
      - (0.5) R2 - Filtered out 192.168.35.0/29 from Redistribution
      - (0.5) R2 - Created route-map R3-FILTER
  - task: (2 Points ) Filter Red. Routes Using a Route Map to set metric
    results:
      - (0.5) R2 - Configured a prefix list R1-PL
      - (0.5) R2 - Selected 172.16.13.0/27 for metric modification
      - (0) INCORRECT Ensure R3 - Learns 172.16.13.0/27 as a E1
```

### Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

### License

This project is licensed under the MIT License. See the LICENSE file for details.

### Contact

For any questions or suggestions, please contact Carolina Ayala.




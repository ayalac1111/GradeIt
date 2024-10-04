# GradeMaster Feature Development Plan

This document outlines planned modifications and features to be implemented in GradeMaster.

## General Feedback Structure - Ongoing
### **Rationale:**

- **Objective:** Continuously adapt the general feedback structure to meet the evolving needs of faculty and provide more comprehensive insights into student performance.
- **Impact:** Updating the general feedback allows to tailor the output to the specific needs of each course and lab. It ensures that the feedback is not only accurate but also relevant and useful for both instructors and students. This feature helps in making informed decisions about curriculum adjustments and identifying common areas of student difficulty.
- **Priority**: 2
- [x] Create a general feedback structure to:
  - [x] Use a similar feedback structure as for individual students.
  - [x] Keep track of all students' feedback to identify common strengths and weaknesses.
  - [ ] Analyze areas where students collectively faced the most challenges.

## Integration of AND and OR Lines in Grading
### **Rationale:**

- **Objective:** Introduce flexibility in grading by allowing multiple correct solutions or conditions to be tested within the answer key.
- **Impact:** This feature acknowledges that there can be multiple correct approaches to solving a problem in networking and IT, reflecting real-world scenarios. It ensures that students are not unfairly penalized for using a valid alternative method, thereby fostering creativity and critical thinking.
- **Priority**: 3
- [ ] Implement the ability to handle AND and OR lines in the grading scheme:
  - [ ] Allow multiple OR alternatives for each line to grade.
  - [ ] Allow multiple AND additional lines for each line to grade.
  - [ ] Ensure the system can correctly interpret and apply these logical conditions during grading.

## Multiple Variables from Student File
### **Rationale:**

- **Objective:** Expand the flexibility of the grading process by allowing the grading scheme to use and process multiple variables from the `students.csv` file, such as IP addresses, subnet masks, and other relevant configuration details.
- **Impact:** In real-world networking and IT environments, configurations often vary based on multiple parameters that are unique to each individual or scenario. By supporting multiple variables in the grading scheme, this change allows for a more personalized and accurate assessment of each student's work. It ensures that the grading process can handle more complex configurations and scenarios, making the tool more robust and applicable to advanced labs. This feature also aligns the grading process more closely with industry practices, where multiple parameters are commonly used and need to be correctly configured in tandem.
- Priority:  2

- [ ] Read and process multiple variables from the `students.csv` file:
  - [ ] Expand beyond just the U variable to include others such as IP, MASK, etc.
  - [ ] Update the grading scheme to recognize and replace these additional variables.

## Multiple files per student
### **Rationale:**

- **Objective:** Handle complex lab submissions that require students to submit multiple files, such as configurations, scripts, and documentation.
- **Impact:** As lab exercises become more complex, it’s essential to accommodate submissions that go beyond a single file. This feature allows for a more comprehensive evaluation of the students’ work, ensuring that all aspects of their submission are considered and appropriately graded.
- **Priority**: 4

## Create Examples and How-Tos

### **Rationale:**

- **Objective:** Provide faculty with detailed examples and instructional materials to help them understand and effectively use the GradeMaster script.
- **Impact:** Offering clear examples and step-by-step guides will make it easier for faculty to adopt the tool, reducing the learning curve and increasing the likelihood of consistent and accurate grading across different lab sessions. This will also empower faculty to create their own answer keys and grading schemes, enhancing the tool’s utility and flexibility.

## Detailed Changes
- [x] Review and update all relevant parts of the codebase to ensure seamless integration of new features. @completed(2024-09-12T10:08:57-04:00)
- [x] Ensure backward compatibility with existing functionalities where applicable. @completed(2024-09-12T10:08:54-04:00)
- [x] Thoroughly test each feature to ensure accuracy and reliability. @completed(2024-09-12T10:09:05-04:00)

This plan will guide the development and enhancement of GradeMaster to make it more versatile and user-friendly.

## **Completed**

## Student Feedback Structure Modifications
### **Rationale:**
- **Objective:** Introduce students to the YAML file format, which is widely used in automation and configuration management.
- **Impact:** By exposing students to YAML, we prepare them for industry-standard tools and practices, such as Ansible and Kubernetes, where YAML is frequently used. It also facilitates easier data manipulation and integration with other tools or scripts in an automated environment.
- **Priority**:  1
- [x] Create a YAML feedback structure for each student.
	- [x] Course information
	- [x] Lab Information
	- [x] Student Feedback
		- [x] Task name
		- [x] Line ( should be called something else )
		- [x] Points
		- [x] Feedback ( if the points were 0 )
- [x] Modify student feedback structure:
  - [x] Create an array per task of 1 or 0 instead of duplicating details/feedback from the `answer_key`.
  - [x] Update all functions that handle the student feedback structure to accommodate this new format.
## Command Line Modifications
- [x] Modify command line options to include:
  - [x] Read `answer_key` name (instead of assuming a fixed name).
  - [x] Read student directory name, where student data will be.
  - [x] Determine how to handle the `students.csv` file, whether it should be passed as a command line argument.

## Feedback Directory Modifications
- [x] Modify the directory where feedback files are created:
  - [x] Option to create a feedback directory at the same level as the student data directory.
  - [x] Option to create a feedback directory inside the student data directory.
## Summary

These modifications aim to enhance the flexibility and usability of the GradeMaster tool by allowing more customization through command line arguments, improving the organization of feedback files, and introducing a more streamlined and insightful feedback system for both individual students and overall student performance analysis.
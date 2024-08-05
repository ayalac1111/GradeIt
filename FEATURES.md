# GradeMaster Feature Development Plan

This document outlines planned modifications and features to be implemented in GradeMaster.

## Command Line Modifications
- [x] Modify command line options to include:
  - [x] Read `answer_key` name (instead of assuming a fixed name).
  - [x] Read student directory name, where student data will be.
  - [x] Determine how to handle the `students.csv` file, whether it should be passed as a command line argument.

## Feedback Directory Modifications
- [x] Modify the directory where feedback files are created:
  - [x] Option to create a feedback directory at the same level as the student data directory.
  - [x] Option to create a feedback directory inside the student data directory.

## Student Feedback Structure Modifications
- [x] Modify student feedback structure:
  - [x] Create an array per task of 1 or 0 instead of duplicating details/feedback from the `answer_key`.
  - [x] Update all functions that handle the student feedback structure to accommodate this new format.

## General Feedback Structure
- [x] Create a general feedback structure to:
  - [ ] Use a similar feedback structure as for individual students.
  - [ ] Keep track of all students' feedback to identify common strengths and weaknesses.
  - [ ] Analyze areas where students collectively faced the most challenges.

## Integration of AND and OR Lines in Grading
- [ ] Implement the ability to handle AND and OR lines in the grading scheme:
  - [ ] Allow multiple OR alternatives for each line to grade.
  - [ ] Allow multiple AND additional lines for each line to grade.
  - [ ] Ensure the system can correctly interpret and apply these logical conditions during grading.

## Multiple Variables from Student File
- [ ] Read and process multiple variables from the `students.csv` file:
  - [ ] Expand beyond just the U variable to include others such as IP, MASK, etc.
  - [ ] Update the grading scheme to recognize and replace these additional variables.

## Detailed Changes
- [ ] Review and update all relevant parts of the codebase to ensure seamless integration of new features.
- [ ] Ensure backward compatibility with existing functionalities where applicable.
- [ ] Thoroughly test each feature to ensure accuracy and reliability.

This plan will guide the development and enhancement of GradeMaster to make it more versatile and user-friendly.

## Summary

These modifications aim to enhance the flexibility and usability of the GradeMaster tool by allowing more customization through command line arguments, improving the organization of feedback files, and introducing a more streamlined and insightful feedback system for both individual students and overall student performance analysis.
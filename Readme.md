# Assignment grader 

A python script / gui for assisting with grading of 
written exam sets / projects.

Launch the program using the following command, with the filenames updated to the proper values.

```
python3 assignment_grader.py --questions questions.txt --students students.txt --grades testing.csv
```

# File descriptions

## students.txt
The file is read by the program and contains ids / names of the students.

## questions.txt
The file is read by the program and contains ids / names of questions.
Usually in the format "number letter", like "3b" and "1c".

## testing.csv
This file is generated by the program and contains a list of all part evaluations
of the assignments.


# Typical usage pattern

1. Download assignments from blackboard (use download in folders) 
   and unpack them in a new directory (here called handins).

2. Clone the assignment-grader git project inside the handins folder
```
cd handins
git clone git@github.com:henrikmidtiby/assignment-grader.git
cd assignment-grader
pipenv install
```

It might be needed to install the following development libraries.
```
sudo apt install libcairo2-dev
sudo apt install libgirepository1.0-dev
```

3. Create a list of assignment ids and save it in the students.txt file

```
ls > students.txt
```

Remove ids from the file that does not match students.

4. Create a list of part assessments (questions / subquestions)

Save the list in the file `questions.txt`.

The file must be structured with three columns like this:
```
1a	5	Recreate figure
1b	6	Describe content of figure
2a	2	Second exercise description
```
The first column is the question id, 
the second column is the weight assigned to the question and 
the third column is a description of question


5. Fill in rubric answers / grades in the `grades.txt` file.

This step is optional.
Can be simplified by using the `prefill-grades-rubrick.Rmd` which is 
in the assignment-grader git repository.

6. Launch the assignment-grader program

```
cd assignment-grader
pipenv run python assignment_grader.py --student ../students.txt --questions ../questions.txt --grades ../grades.txt
```

7. Parse the generated grades.csv file using a suitable R document / script like `collectedComments.Rnw`.

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
```

3. Create a list of assignment ids and save it in the students.txt file

```
ls > students.txt
```

Remove ids from the file that does not match students.

4. Create a list of part assessments (questions / subquestions)

The file could be structured like this
```
1a	Recreate figure
1b	Describe content of figure
2a	Second exercise description
```

5. Launch the assignment-grader program

```
cd assignment-grader
python assignment-grader.py --student ../students.txt --questions ../questions.txt --grades ../grades.csv
```

6. Parse the generated grades.csv file using a suitable R document / script.
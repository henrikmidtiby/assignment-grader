mypytests: 
	pipenv run mypy assignment_grader.py

default:
	pipenv run python assignment_grader.py --student ../students.txt --questions ../questions.txt --grades ../grades.txt

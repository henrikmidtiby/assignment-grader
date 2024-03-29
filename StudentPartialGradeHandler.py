import collections
import re

ScoreAndReason = collections.namedtuple('ScoreAndReason', ['score', 'reason'])


class StudentPartialGradeHandler:
    def load_list_of_reasons(self, filename: str):
        self.dict_of_score_and_reasons: dict = collections.defaultdict(lambda: collections.defaultdict(list))
        for (student_id, question, point, reason) in self.extract_reasons_from_file(filename):
            self.dict_of_score_and_reasons[student_id][question] = ScoreAndReason(point, reason)
        self.rebuild_dict_of_reasons()

    def rebuild_dict_of_reasons(self):
        self.dict_of_reasons = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
        for student, question, point, reason in self.get_question_point_and_reasons_from_dict_of_scores_and_reasons():
            self.dict_of_reasons[question][point][reason] += 1

    def get_question_point_and_reasons_from_dict_of_scores_and_reasons(self):
        for student_id in self.dict_of_score_and_reasons.keys():
            student_partial_grades = self.dict_of_score_and_reasons[student_id]
            for question_id in student_partial_grades.keys():
                question_partial_grades = student_partial_grades[question_id]
                yield student_id, question_id, str(question_partial_grades.score), question_partial_grades.reason

    @staticmethod
    def extract_reasons_from_file(filename: str):
        # agreg15	1a	2	Punkterne
        pattern = re.compile('(.*)\t(.*)\t(\d+)\t(.*)')
        try:
            with open(filename) as file_handle:
                for line in file_handle:
                    res = pattern.match(line)
                    if res:
                        student_id = res.group(1)
                        question = res.group(2)
                        point = int(res.group(3))
                        reason = res.group(4)
                        yield (student_id, question, point, reason)
        except FileNotFoundError:
            print("File not found '%s'." % filename)

    def save_reasons_to_a_file(self, filename: str):
        print("save_reasons_to_a_file")
        with open(filename, 'w') as file_handle:
            for student_id, question_id, points, reason in self.get_evaluation_lines_for_export_to_file():
                print("%s\t%s\t%s\t%s" % (student_id, question_id, points, reason),
                      file = file_handle)

    def get_evaluation_lines_for_export_to_file(self):
        for student_id in sorted(self.dict_of_score_and_reasons.keys()):
            student_scores = self.dict_of_score_and_reasons[student_id]
            for question_id in sorted(student_scores.keys()):
                score = student_scores[question_id].score
                reason = student_scores[question_id].reason
                yield student_id, question_id, score, reason

    def set_partial_grades(self, student_id: str, partial_grades: list):
        assert(student_id is not None)
        self.dict_of_score_and_reasons[student_id].clear()
        for grade in partial_grades:
            if type(grade.grade) == "str":
                try:
                    grade.grade = int(grade.grade)
                except Exception as e:
                    print(e)
                    print(grade.grade)
                    print(grade.reason)
                    grade.grade = 0
            score_and_reason = ScoreAndReason(grade.grade, grade.reason)
            self.dict_of_score_and_reasons[student_id][grade.question_id] = score_and_reason
        self.rebuild_dict_of_reasons()

    def get_partial_grades(self, student_id):
        return dict(self.dict_of_score_and_reasons[student_id])



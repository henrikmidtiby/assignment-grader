import collections
import re

ScoreAndReason = collections.namedtuple('ScoreAndReason', ['score', 'reason'])


class StudentPartialGradeHandler:
    def load_list_of_reasons(self, filename):
        self.dict_of_reasons = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
        self.dict_of_score_and_reasons = collections.defaultdict(lambda: collections.defaultdict(list))
        for (student_id, question, point, reason) in self.extract_reasons_from_file(filename):
            self.dict_of_reasons[question][point][reason] += 1
            self.dict_of_score_and_reasons[student_id][question] = ScoreAndReason(point, reason)

    @staticmethod
    def extract_reasons_from_file(filename):
        # agreg15	1a	2	Punkterne
        pattern = re.compile('(.*)\t(.*)\t(\d+)\t(.*)')
        with open(filename) as file_handle:
            for line in file_handle:
                res = pattern.match(line)
                if res:
                    student_id = res.group(1)
                    question = res.group(2)
                    point = int(res.group(3))
                    reason = res.group(4)
                    yield (student_id, question, point, reason)

    def save_reasons_to_a_file(self, filename):
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

    def set_partial_grades(self, student_id, partial_grades):
        self.dict_of_score_and_reasons[student_id].clear()
        for grade in partial_grades:
            score_and_reason = ScoreAndReason(grade.grade, grade.reason)
            self.dict_of_score_and_reasons[student_id][grade.question_id] = score_and_reason



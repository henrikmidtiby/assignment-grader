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
            student_id = self.current_student_id
            for row in range(self.grid_k):
                question_id = self.grid_labels[row].get_text()
                points = self.grid_points[row].get_text()
                reason = self.grid_reasons[row].get_text()
                print("%s\t%s\t%s\t%s" % (student_id, question_id, points, reason),
                      file = file_handle)

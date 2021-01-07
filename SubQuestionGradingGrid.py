import re
import collections
import gi
from typing import List
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

StudentAndPartialGrades = collections.namedtuple('StudentAndPartialGrades', ['student_id', 'partial_grades'])
QuestionGradeAndReason = collections.namedtuple('QuestionGradeAndReason', ['question_id', 'grade', 'reason'])


class SubQuestionGradingGrid(Gtk.Grid):
    __gsignals__ = {
        'sub_question_line_has_changed': (GObject.SIGNAL_RUN_FIRST, None,
                      ())
    }

    def __init__(self, file_with_question_names: str) -> None:
        Gtk.Grid.__init__(self)
        self.add_grid_with_entry_fields(file_with_question_names)

    def add_grid_with_entry_fields(self, file_with_question_names: str):
        self.set_size_request(550, -1)
        self.set_column_spacing(10)
        self.add_column_headers_for_entry_rows()
        self.reset_grid_data_structure()
        self.add_rows_to_grid(file_with_question_names)

    def add_column_headers_for_entry_rows(self):
        self.grid_header_label = Gtk.Label("Question")
        self.grid_header_point = Gtk.Label("Point")
        self.grid_header_reason = Gtk.Label("Reason")
        self.attach(self.grid_header_label, 0, 0, 1, 1)
        self.attach(self.grid_header_point, 1, 0, 1, 1)
        self.attach(self.grid_header_reason, 2, 0, 1, 1)

    def reset_grid_data_structure(self):
        self.grid_labels = []
        self.grid_points = []
        self.grid_reasons = []
        self.eval_indicators = []
        self.grid_k = 1

    def add_rows_to_grid(self, file_with_question_names: str):
        for question, weight, description in self.extract_questions_from_file(file_with_question_names):
            self.add_row_of_entry_fields(question, "%s -- %s point" % (description, weight))

    @staticmethod
    def extract_questions_from_file(file_with_question_names: str):
        with open(file_with_question_names) as file_handle:
            for line in file_handle:
                pattern = re.compile("(\d[a-z]\d*)\s+(\d*)\s*(.*)")
                res = pattern.match(line)
                if res:
                    question = res.group(1)
                    weight = res.group(2)
                    description = res.group(3)
                    yield question, weight, description

    def add_row_of_entry_fields(self, question: str, description: str):
        entry_point_min_width = 4
        entry_reason_min_width = 50

        self.add_new_question_entry_in_grid(question, description)
        self.add_new_point_entry_in_grid(entry_point_min_width)
        self.add_new_reason_entry_in_grid(entry_reason_min_width)
        self.add_new_color_box_entry_in_grid()
        self.grid_k += 1

    def add_new_question_entry_in_grid(self, question: str, description: str):
        question_id = Gtk.Label(question)
        question_id.set_tooltip_text(description)
        self.attach(question_id, 0, self.grid_k, 1, 1)
        self.grid_labels.append(question_id)

    def add_new_point_entry_in_grid(self, entry_point_min_width: float):
        point = Gtk.Entry()
        point.set_width_chars(entry_point_min_width)
        point.connect('event', self.event_catcher, self.grid_k)
        self.attach(point, 1, self.grid_k, 1, 1)
        self.grid_points.append(point)
        return point

    def add_new_reason_entry_in_grid(self, entry_reason_min_width: float):
        reason = Gtk.Entry()
        reason.set_width_chars(entry_reason_min_width)
        reason.connect('event', self.event_catcher, self.grid_k)
        self.attach(reason, 2, self.grid_k, 1, 1)
        self.grid_reasons.append(reason)

    def add_new_color_box_entry_in_grid(self):
        progressbar = Gtk.ProgressBar()
        self.attach(progressbar, 3, self.grid_k, 1, 1)
        self.eval_indicators.append(progressbar)

    def event_catcher(self, entry, event, k: int):
        if event.type == Gdk.EventType.FOCUS_CHANGE:
            self.last_updated_row = k - 1
            self.emit("sub_question_line_has_changed")

    def get_question_id_of_last_active_row(self) -> str:
        return self.grid_labels[self.last_updated_row].get_text()

    def get_question_description_of_last_active_row(self) -> str:
        return self.grid_labels[self.last_updated_row].get_tooltip_text()

    def get_points_for_subquestion_of_last_active_row(self):
        point_str = self.grid_points[self.last_updated_row].get_text()
        try:
            point = int(point_str)
        except ValueError as e:
            point = None
        return point

    def set_points_for_subquestion_of_last_active_row(self, points):
        return self.grid_points[self.last_updated_row].set_text("%d" % points)

    def set_reason_for_subquestion_of_last_active_row(self, reason):
        return self.grid_reasons[self.last_updated_row].set_text(reason)

    def advance_active_row(self):
        self.emit("sub_question_line_has_changed")
        try:
            self.grid_points[self.last_updated_row + 1].grab_focus()
        except IndexError:
            print("Warning: Not possible to advance to next question.")

    def get_all_partial_grades(self) -> List[QuestionGradeAndReason]:
        partial_grades = []
        for k in range(self.grid_k):
            partial_grade = self.get_partial_grade(k)
            partial_grades.append(partial_grade)
        return partial_grades

    def get_partial_grade(self, k: int) -> QuestionGradeAndReason:
        k = k - 1
        question_id = self.grid_labels[k].get_text()
        point = self.grid_points[k].get_text()
        reason = self.grid_reasons[k].get_text()
        partial_grade = QuestionGradeAndReason(question_id, point, reason)
        return partial_grade

    def clean_all_fields(self):
        for k in range(self.grid_k):
            self.grid_points[k - 1].set_text("")
            self.grid_reasons[k - 1].set_text("")

    def set_fields_to_previous_values(self, values: dict):
        for k in range(self.grid_k - 1):
            try:
                question_id = self.grid_labels[k].get_text()
                points = values[question_id].score
                self.eval_indicators[k].set_fraction(points / 10)
                comment = values[question_id].reason
                self.grid_points[k].set_text(str(points))
                self.grid_reasons[k].set_text(comment)
            except KeyError as e:
                pass
            except Exception as e:
                print("Exception")

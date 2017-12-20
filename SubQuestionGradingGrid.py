import re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject



class SubQuestionGradingGrid(Gtk.Grid):
    __gsignals__ = {
        'sub_question_line_has_changed': (GObject.SIGNAL_RUN_FIRST, None,
                      (int,))
    }

    def __init__(self, file_with_question_names):
        Gtk.Grid.__init__(self)
        self.add_grid_with_entry_fields(file_with_question_names)

    def add_grid_with_entry_fields(self, file_with_question_names):
        self.set_size_request(900, -1)
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
        self.grid_k = 1

    def add_rows_to_grid(self, file_with_question_names):
        for question in self.extract_questions_from_file(file_with_question_names):
            self.add_row_of_entry_fields(question)

    @staticmethod
    def extract_questions_from_file(file_with_question_names):
        with open(file_with_question_names) as file_handle:
            for line in file_handle:
                pattern = re.compile("(\d[a-z])")
                res = pattern.match(line)
                if res:
                    question = res.group(1)
                    yield question

    def add_row_of_entry_fields(self, question):
        entry_label_min_width = 4
        entry_point_min_width = 4
        entry_reason_min_width = 60

        self.add_new_question_entry_in_grid(entry_label_min_width, question)
        self.add_new_point_entry_in_grid(entry_point_min_width)
        self.add_new_reason_entry_in_grid(entry_reason_min_width)
        self.grid_k += 1

    def add_new_question_entry_in_grid(self, entry_label_min_width, question):
        question_id = Gtk.Entry()
        question_id.set_width_chars(entry_label_min_width)
        question_id.set_text(question)
        #question_id.connect("changed", self.question_id_has_changed, self.grid_k)
        self.attach(question_id, 0, self.grid_k, 1, 1)
        self.grid_labels.append(question_id)

    def add_new_point_entry_in_grid(self, entry_point_min_width):
        point = Gtk.Entry()
        point.set_width_chars(entry_point_min_width)
        # point.connect("changed", self.points_has_changed, self.grid_k)
        point.connect('event', self.event_catcher, self.grid_k)
        self.attach(point, 1, self.grid_k, 1, 1)
        self.grid_points.append(point)
        return point

    def add_new_reason_entry_in_grid(self, entry_reason_min_width):
        reason = Gtk.Entry()
        reason.set_width_chars(entry_reason_min_width)
        #reason.connect("changed", self.reason_has_changed, self.grid_k)
        self.attach(reason, 2, self.grid_k, 1, 1)
        self.grid_reasons.append(reason)

    def event_catcher(self, entry, event, k):
        print(event.type, k)
        self.emit("sub_question_line_has_changed", k)

    def get_question_id(self, row_number):
        return self.grid_labels[row_number].get_text()

    def get_points_for_subquestion(self, row_number):
        return self.grid_points[row_number].get_text()
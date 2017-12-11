import collections
import re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


GradedQuestion = collections.namedtuple('GradedQuestion', ['student', 'question', 'point', 'reason'])


class MyWindow(Gtk.Window):

    def __init__(self, file_with_question_names):
        Gtk.Window.__init__(self, title="Assignment grader")

        self.h_box = Gtk.Box(spacing=6)
        self.add(self.h_box)

        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(10)

        self.add_column_headers_for_entry_rows()

        questions = ['1a', '1b', '2a', '2b', '2c']
        self.reset_grid_data_structure()
        self.add_rows_to_grid(file_with_question_names)
        self.h_box.pack_start(self.grid, True, True, 0)

        self.add_list_of_reasons_widget()

    def add_rows_to_grid(self, file_with_question_names):
        with open(file_with_question_names) as file_handle:
            for line in file_handle:
                pattern = re.compile("(\d[a-z])")
                res = pattern.match(line)
                if res:
                    question = res.group(1)
                    self.add_row_of_entry_fields(question)
        self.add_row_of_entry_fields('')

    def reset_grid_data_structure(self):
        self.grid_labels = []
        self.grid_points = []
        self.grid_reasons = []
        self.grid_k = 1

    def add_list_of_reasons_widget(self):
        self.list_of_reasons_buffer = Gtk.TextBuffer()
        self.list_of_reasons = Gtk.TextView()
        self.list_of_reasons.set_buffer(self.list_of_reasons_buffer)
        self.list_of_reasons_buffer.set_text('This is a test.\nSeveral lines...')
        self.reason_tag = self.list_of_reasons_buffer.create_tag('reason_tag')
        self.reason_tag.connect('event', self.click_in_list_of_reasons)
        self.h_box.pack_start(self.list_of_reasons, True, True, 0)

    def add_column_headers_for_entry_rows(self):
        self.grid_header_label = Gtk.Label("Question")
        self.grid_header_point = Gtk.Label("Point")
        self.grid_header_reason = Gtk.Label("Reason")
        self.grid.attach(self.grid_header_label, 0, 0, 1, 1)
        self.grid.attach(self.grid_header_point, 1, 0, 1, 1)
        self.grid.attach(self.grid_header_reason, 2, 0, 1, 1)

    def add_row_of_entry_fields(self, question):
        entry_label_min_width = 4
        entry_point_min_width = 4
        entry_reason_min_width = 40

        question_id = Gtk.Entry()
        question_id.set_max_width_chars(entry_label_min_width)
        point = Gtk.Entry()
        point.set_width_chars(entry_point_min_width)
        reason = Gtk.Entry()
        reason.set_width_chars(entry_reason_min_width)
        question_id.set_text(question)
        question_id.connect("changed", self.question_id_has_changed, self.grid_k)
        point.connect("changed", self.points_has_changed, self.grid_k)
        reason.connect("changed", self.reason_has_changed, self.grid_k)
        self.grid.attach(question_id, 0, self.grid_k, 1, 1)
        self.grid.attach(point, 1, self.grid_k, 1, 1)
        self.grid.attach(reason, 2, self.grid_k, 1, 1)
        self.grid_labels.append(question_id)
        self.grid_points.append(point)
        self.grid_reasons.append(reason)
        self.grid_k += 1

    def question_id_has_changed(self, widget, k):
        self.update_list_of_reasons_based_on_a_single_row(k)

    def points_has_changed(self, widget, k):
        self.update_list_of_reasons_based_on_a_single_row(k)

    def reason_has_changed(self, widget, k):
        pass

    def update_list_of_reasons_based_on_a_single_row(self, k):
        self.last_updated_row = k - 1
        question_id = self.grid_labels[self.last_updated_row].get_text()
        point_str = self.grid_points[self.last_updated_row].get_text()
        try:
            point = int(point_str)
        except ValueError as e:
            point = None
        self.update_list_of_reasons(question_id, point)

    def update_list_of_reasons(self, question, point):
        self.list_of_reasons_buffer.set_text('')
        if point is None:
            for point_key in self.dict_of_reasons[question]:
                for reason_key in self.dict_of_reasons[question][point_key]:
                    self.insert_point_and_reason_in_list(question, point_key, reason_key)
        else:
            for reason_key in self.dict_of_reasons[question][point]:
                self.insert_point_and_reason_in_list(question, point, reason_key)

    def insert_point_and_reason_in_list(self, question, point, reason):
        multiplicity = self.dict_of_reasons[question][point][reason]
        end_iter = self.list_of_reasons_buffer.get_end_iter()
        new_reason = "%2d (%s) - %s" % (point, multiplicity, reason)
        self.list_of_reasons_buffer.insert_with_tags(end_iter, new_reason, self.reason_tag)
        self.list_of_reasons_buffer.insert(end_iter, "\n")

    def load_list_of_reasons(self, filename):
        self.dict_of_reasons = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
        # agreg15	1a	2	Punkterne
        pattern = re.compile('(.*)\t(.*)\t(\d+)\t(.*)')
        with open(filename) as file_handle:
            for line in file_handle:
                res = pattern.match(line)
                if res:
                    question = res.group(2)
                    point = int(res.group(3))
                    reason = res.group(4)
                    self.dict_of_reasons[question][point][reason] += 1

    def click_in_list_of_reasons(self, tag, widget, event, iter):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            clicked_reason = self.get_content_of_reason_tag_indicated_by_iter(iter)
            self.update_reason_for_current_question(clicked_reason)

    def get_content_of_reason_tag_indicated_by_iter(self, iter):
        end_iter = iter.copy()
        end_iter.forward_to_tag_toggle(self.reason_tag)
        iter.backward_to_tag_toggle(self.reason_tag)
        clicked_reason = self.list_of_reasons_buffer.get_text(iter, end_iter, False)
        return clicked_reason

    def update_reason_for_current_question(self, clicked_reason):
        pattern = re.compile('\s*(\d+) \(\d+\) - (.*)')
        res = pattern.match(clicked_reason)
        if res:
            point = res.group(1)
            reason = res.group(2)
            self.grid_points[self.last_updated_row].set_text(point)
            self.grid_reasons[self.last_updated_row].set_text(reason)


win = MyWindow('questions.txt')
win.connect("delete-event", Gtk.main_quit)
win.show_all()
win.load_list_of_reasons('statistics.csv')
win.update_list_of_reasons('1a', 0)
Gtk.main()
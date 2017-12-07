import collections
import re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


GradedQuestion = collections.namedtuple('GradedQuestion', ['student', 'question', 'point', 'reason'])


class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Assignment grader")

        self.h_box = Gtk.Box(spacing=6)
        self.add(self.h_box)

        entry_label_min_width = 4
        entry_point_min_width = 4
        entry_reason_min_width = 40

        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(10)

        self.grid_header_label = Gtk.Label("Question")
        self.grid_header_point = Gtk.Label("Point")
        self.grid_header_reason = Gtk.Label("Reason")
        self.grid.attach(self.grid_header_label, 0, 0, 1, 1)
        self.grid.attach(self.grid_header_point, 1, 0, 1, 1)
        self.grid.attach(self.grid_header_reason, 2, 0, 1, 1)

        self.grid_labels = []
        self.grid_points = []
        self.grid_reasons = []
        for k in range(1, 10):
            question_id = Gtk.Entry()
            question_id.connect("changed", self.question_id_has_changed, k)
            question_id.set_max_width_chars(entry_label_min_width)
            point = Gtk.Entry()
            point.connect("changed", self.points_has_changed, k)
            point.set_width_chars(entry_point_min_width)
            reason = Gtk.Entry()
            reason.connect("changed", self.reason_has_changed, k)
            reason.set_width_chars(entry_reason_min_width)
            self.grid.attach(question_id, 0, k, 1, 1)
            self.grid.attach(point, 1, k, 1, 1)
            self.grid.attach(reason, 2, k, 1, 1)
            self.grid_labels.append(question_id)
            self.grid_points.append(point)
            self.grid_reasons.append(reason)

        self.h_box.pack_start(self.grid, True, True, 0)

        self.list_of_reasons_buffer = Gtk.TextBuffer()
        self.list_of_reasons = Gtk.TextView()
        self.list_of_reasons.set_buffer(self.list_of_reasons_buffer)
        self.list_of_reasons_buffer.set_text('This is a test.\nSeveral lines...')
        self.reason_tag = self.list_of_reasons_buffer.create_tag('reason_tag')
        self.reason_tag.connect('event', self.click_in_list_of_reasons)
        self.h_box.pack_start(self.list_of_reasons, True, True, 0)

    def question_id_has_changed(self, widget, k):
        self.update_list_of_reasons_based_on_a_single_row(k)

    def points_has_changed(self, widget, k):
        self.update_list_of_reasons_based_on_a_single_row(k)

    def reason_has_changed(self, widget, k):
        pass

    def update_list_of_reasons_based_on_a_single_row(self, k):
        question_id = self.grid_labels[k - 1].get_text()
        point_str = self.grid_points[k - 1].get_text()
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
                    student = res.group(1)
                    question = res.group(2)
                    point = int(res.group(3))
                    reason_temp = res.group(4)
                    reason = GradedQuestion(student=student,
                                            question=question,
                                            point=point,
                                            reason=reason_temp)
                    self.dict_of_reasons[question][point][reason_temp] += 1
        # print("Has loaded %d answers." % len(self.long_list_of_reasons))

    def click_in_list_of_reasons(self, tag, widget, event, iter):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            end_iter = iter.copy()
            end_iter.forward_to_tag_toggle(self.reason_tag)
            iter.backward_to_tag_toggle(self.reason_tag)
            clicked_reason = self.list_of_reasons_buffer.get_text(iter, end_iter, False)
            print(clicked_reason)


win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
win.load_list_of_reasons('statistics.csv')
win.update_list_of_reasons('1a', 0)
Gtk.main()
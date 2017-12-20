import collections
import re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import StudentPartialGradeHandler
import SubQuestionGradingGrid

class MyWindow(Gtk.Window):

    def __init__(self, file_with_question_names, file_with_student_names):
        self.student_partial_grade_handler = StudentPartialGradeHandler.StudentPartialGradeHandler()
        Gtk.Window.__init__(self, title="Assignment grader")
        self.resize(1300, 700)

        self.v_box = Gtk.VBox()
        self.add(self.v_box)
        self.add_student_selector(file_with_student_names)
        self.add_save_button()
        self.add_grid_entry_and_reason_list(file_with_question_names)

    def add_student_selector(self, file_with_student_names):
        self.load_list_of_students(file_with_student_names)
        self.add_combo_box_with_student_names_from_name_store()

    def load_list_of_students(self, filename):
        self.name_store = Gtk.ListStore(str)

        pattern = re.compile('(.*)')
        with open(filename) as file_handle:
            for line in file_handle:
                res = pattern.match(line)
                if res:
                    student_id = res.group(1)
                    self.name_store.append([student_id])

    def add_combo_box_with_student_names_from_name_store(self):
        self.current_student_id = None
        self.name_combo = Gtk.ComboBox.new_with_model(self.name_store)
        renderer_text = Gtk.CellRendererText()
        self.name_combo.pack_start(renderer_text, True)
        self.name_combo.add_attribute(renderer_text, "text", 0)
        self.name_combo.connect("changed", self.on_name_combo_changed)
        self.v_box.pack_start(self.name_combo, False, False, 0)

    def on_name_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            student_id = model[tree_iter][0]
            self.current_student_id = student_id

    def add_save_button(self):
        button = Gtk.Button.new_with_label("Save")
        button.connect("clicked", self.on_save_button_clicked)
        self.v_box.pack_start(button, False, False, 0)

    def on_save_button_clicked(self, t1):
        self.student_partial_grade_handler.save_reasons_to_a_file('testing.csv')

    def add_grid_entry_and_reason_list(self, file_with_question_names):
        self.h_box = Gtk.HBox(spacing=6)
        self.grid_with_entry = SubQuestionGradingGrid.SubQuestionGradingGrid(file_with_question_names)
        self.grid_with_entry.connect('sub_question_line_has_changed', self.simple_event_catcher)
        self.h_box.pack_start(self.grid_with_entry, False, False, 0)
        self.add_list_of_reasons_widget()
        self.v_box.pack_start(self.h_box, False, False, 0)

    def simple_event_catcher(self, place_holder, k):
        self.update_list_of_reasons_based_on_a_single_row(k)

    def update_list_of_reasons_based_on_a_single_row(self, k):
        self.last_updated_row = k - 1
        question_id = self.grid_with_entry.get_question_id(self.last_updated_row)
        point_str = self.grid_with_entry.get_points_for_subquestion(self.last_updated_row)
        try:
            point = int(point_str)
        except ValueError as e:
            point = None
        self.update_list_of_reasons(question_id, point)

    def update_list_of_reasons(self, question, point):
        self.list_of_reasons_buffer.set_text('')
        if point is None:
            for point_key in self.student_partial_grade_handler.dict_of_reasons[question]:
                self.given_point_insert_all_matching_reasons(point_key, question)
        else:
            self.given_point_insert_all_matching_reasons(point - 1, question)
            self.given_point_insert_all_matching_reasons(point, question)
            self.given_point_insert_all_matching_reasons(point + 1, question)

    def given_point_insert_all_matching_reasons(self, point, question):
        for reason_key in self.student_partial_grade_handler.dict_of_reasons[question][point]:
            self.insert_point_and_reason_in_list(question, point, reason_key)

    def insert_point_and_reason_in_list(self, question, point, reason):
        multiplicity = self.student_partial_grade_handler.dict_of_reasons[question][point][reason]
        end_iter = self.list_of_reasons_buffer.get_end_iter()
        new_reason = "%2d (%s) - %s" % (point, multiplicity, reason)
        self.list_of_reasons_buffer.insert_with_tags(end_iter, new_reason, self.reason_tag)
        self.list_of_reasons_buffer.insert(end_iter, "\n")

    def add_list_of_reasons_widget(self):
        self.list_of_reasons_buffer = Gtk.TextBuffer()
        self.list_of_reasons = Gtk.TextView()
        self.list_of_reasons.set_editable(False)
        self.list_of_reasons.set_cursor_visible(False)
        self.list_of_reasons.set_buffer(self.list_of_reasons_buffer)
        self.list_of_reasons_buffer.set_text('')
        self.reason_tag = self.list_of_reasons_buffer.create_tag('reason_tag')
        self.reason_tag.connect('event', self.click_in_list_of_reasons)
        self.h_box.pack_start(self.list_of_reasons, False, False, 0)

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

    def load_list_of_reasons(self, filename):
        self.student_partial_grade_handler.load_list_of_reasons(filename)

win = MyWindow('questions.txt', 'students.txt')
win.connect("delete-event", Gtk.main_quit)
win.show_all()
win.load_list_of_reasons('statistics.csv')
Gtk.main()
import re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import StudentPartialGradeHandler
import SubQuestionGradingGrid
import ListOfReasonsWidget


class AssignmentGrader(Gtk.Window):

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
        current_partial_grades = self.grid_with_entry.get_all_partial_grades()
        print(current_partial_grades)
        # Todo: Save list of grades
        self.student_partial_grade_handler.save_reasons_to_a_file('testing.csv')

    def add_grid_entry_and_reason_list(self, file_with_question_names):
        self.h_box = Gtk.HBox(spacing=6)
        self.add_grid_entry_widget(file_with_question_names)
        self.add_list_of_reasons_widget()
        self.v_box.pack_start(self.h_box, False, False, 0)

    def add_grid_entry_widget(self, file_with_question_names):
        self.grid_with_entry = SubQuestionGradingGrid.SubQuestionGradingGrid(file_with_question_names)
        self.grid_with_entry.connect('sub_question_line_has_changed', self.update_list_of_reasons_based_on_a_single_row)
        self.h_box.pack_start(self.grid_with_entry, False, False, 0)

    def update_list_of_reasons_based_on_a_single_row(self, placeholder):
        partial_grades = self.grid_with_entry.get_all_partial_grades()
        student_id = self.current_student_id
        self.student_partial_grade_handler.set_partial_grades(student_id, partial_grades)
        # Todo: Update list of reasons in self.student_partial_grade_handler so the data can be saved afterwards.
        question_id = self.grid_with_entry.get_question_id_of_last_active_row()
        point = self.grid_with_entry.get_points_for_subquestion_of_last_active_row()
        self.list_of_reasons.update_list_of_reasons(question_id, point, self.student_partial_grade_handler)

    def add_list_of_reasons_widget(self):
        self.list_of_reasons = ListOfReasonsWidget.ListOfReasonsWidget()
        self.list_of_reasons.connect('reason_selected', self.update_reason_for_current_question)
        self.h_box.pack_start(self.list_of_reasons, False, False, 0)

    def update_reason_for_current_question(self, placeholder, point, reason):
        self.grid_with_entry.set_points_for_subquestion_of_last_active_row(point)
        self.grid_with_entry.set_reason_for_subquestion_of_last_active_row(reason)

    def load_list_of_reasons(self, filename):
        self.student_partial_grade_handler.load_list_of_reasons(filename)

win = AssignmentGrader('questions.txt', 'students.txt')
win.connect("delete-event", Gtk.main_quit)
win.show_all()
win.load_list_of_reasons('statistics.csv')
Gtk.main()
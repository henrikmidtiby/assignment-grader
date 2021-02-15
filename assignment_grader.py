import re
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio
import argparse
import StudentPartialGradeHandler
import SubQuestionGradingGrid
import ListOfReasonsWidget
from DebugDecorator import debug


MENU_XML = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="app-menu">
    <section>
      <item>
        <attribute name="action">app.next_item</attribute>
        <attribute name="label" translatable="yes">_Next item</attribute>
        <attribute name="accel">&lt;Primary&gt;n</attribute>
      </item>
      <item>
        <attribute name="action">app.previous_item</attribute>
        <attribute name="label" translatable="yes">_Previous item</attribute>
        <attribute name="accel">&lt;Primary&gt;p</attribute>
      </item>
      <item>
        <attribute name="action">app.quit</attribute>
        <attribute name="label" translatable="yes">_Quit</attribute>
        <attribute name="accel">&lt;Primary&gt;q</attribute>
      </item>
    </section>
  </menu>
</interface>
"""


class AssignmentGrader(Gtk.ApplicationWindow):
    def __init__(self, app, file_with_question_names: str, file_with_student_names: str, file_with_grades: str) -> None:
        self.student_partial_grade_handler = StudentPartialGradeHandler.StudentPartialGradeHandler()
        self.list_of_reasons = None
        self.grid_with_entry: SubQuestionGradingGrid.SubQuestionGradingGrid = None
        self.h_box: Gtk.HBox = None
        self.current_student_id = None
        self.name_store: list = None
        self.name_combo = None
        self.file_with_grades = file_with_grades
        Gtk.Window.__init__(self, title="Assignment grader", application=app)
        self.resize(1300, 700)

        self.v_box = Gtk.VBox()
        self.add(self.v_box)
        self.add_student_selector(file_with_student_names)
        self.add_save_button()
        self.add_grid_entry_and_reason_list(file_with_question_names)

    def initialise_view(self):
        self.name_combo.set_active(0)

    def add_student_selector(self, file_with_student_names: str):
        self.load_list_of_students(file_with_student_names)
        self.add_combo_box_with_student_names_from_name_store()

    def load_list_of_students(self, filename: str):
        self.name_store = Gtk.ListStore(str, str)
        counter = 0
        pattern = re.compile('(.*)')
        with open(filename) as file_handle:
            for line in file_handle:
                res = pattern.match(line)
                if res:
                    student_id = res.group(1)
                    counter += 1
                    self.name_store.append([student_id, "%s - %d" % (student_id, counter)])

    def add_combo_box_with_student_names_from_name_store(self):
        self.current_student_id = None
        self.name_combo = Gtk.ComboBox.new_with_model(self.name_store)
        renderer_text = Gtk.CellRendererText()
        self.name_combo.pack_start(renderer_text, True)
        self.name_combo.add_attribute(renderer_text, "text", 1)
        self.name_combo.connect("changed", self.on_name_combo_changed)
        self.v_box.pack_start(self.name_combo, False, False, 0)

    def on_name_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            student_id = model[tree_iter][0]
            self.current_student_id = student_id
        self.grid_with_entry.clean_all_fields()
        values = self.student_partial_grade_handler.get_partial_grades(self.current_student_id)
        self.grid_with_entry.set_fields_to_previous_values(values)
        self.grid_with_entry.activate_first_row()
        self.student_partial_grade_handler.save_reasons_to_a_file(self.file_with_grades)

    def add_save_button(self):
        button = Gtk.Button.new_with_label("Save")
        button.connect("clicked", self.on_save_button_clicked)
        self.v_box.pack_start(button, False, False, 0)

    def on_save_button_clicked(self, t1):
        self.student_partial_grade_handler.save_reasons_to_a_file(self.file_with_grades)

    def add_grid_entry_and_reason_list(self, file_with_question_names: str):
        self.h_box = Gtk.HBox(spacing=6)
        self.add_grid_entry_widget(file_with_question_names)
        self.add_list_of_reasons_widget()
        self.v_box.pack_start(self.h_box, True, True, 0)

    def add_grid_entry_widget(self, file_with_question_names: str):
        self.grid_with_entry = SubQuestionGradingGrid.SubQuestionGradingGrid(file_with_question_names)
        self.grid_with_entry.connect('sub_question_line_has_changed', self.update_list_of_reasons_based_on_a_single_row)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_border_width(20)
        self.scrolled_window.set_min_content_width(600)
        self.scrolled_window.set_max_content_width(600)
        self.scrolled_window.set_min_content_height(900)
        self.scrolled_window.set_max_content_height(1500)
        # TODO: Fix this so it is possible to resize the main window.
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_valign(0)
        
        self.scrolled_window.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.scrolled_window.add_with_viewport(self.grid_with_entry)
        self.h_box.pack_start(self.scrolled_window, False, False, 0)

    def update_list_of_reasons_based_on_a_single_row(self, placeholder):
        """
        This method is called when a field for entering partial grades
        is given focus or its content is changed.
        :param placeholder:
        :return:
        """
        partial_grades = self.grid_with_entry.get_all_partial_grades()
        student_id = self.current_student_id
        self.student_partial_grade_handler.set_partial_grades(student_id, partial_grades)
        question_id = self.grid_with_entry.get_question_id_of_last_active_row()
        question_description = self.grid_with_entry.get_question_description_of_last_active_row()
        point = self.grid_with_entry.get_points_for_subquestion_of_last_active_row()
        self.list_of_reasons.update_list_of_reasons(question_id, question_description, point, self.student_partial_grade_handler)

    def add_list_of_reasons_widget(self):
        self.list_of_reasons = ListOfReasonsWidget.ListOfReasonsWidget()
        self.list_of_reasons.connect('reason_selected', self.update_reason_for_current_question)
        self.h_box.pack_start(self.list_of_reasons, False, False, 0)

    def update_reason_for_current_question(self, placeholder, point: int, reason: str):
        self.grid_with_entry.set_points_for_subquestion_of_last_active_row(point)
        self.grid_with_entry.set_reason_for_subquestion_of_last_active_row(reason)
        self.grid_with_entry.advance_active_row()

    def load_list_of_reasons(self, filename: str):
        self.student_partial_grade_handler.load_list_of_reasons(filename)


class MyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.sdu.midtiby.assignment_grader")
        self.question_file = None
        self.student_file = None
        self.grade_file = None

    def set_input_files(self, questions: str, students: str, grades: str):
        self.question_file = questions
        self.student_file = students
        self.grade_file = grades

    def do_activate(self):
        win = AssignmentGrader(self, self.question_file, self.student_file, self.grade_file)
        win.load_list_of_reasons(self.grade_file)
        win.initialise_view()
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        builder = Gtk.Builder.new_from_string(MENU_XML, -1)
        self.set_app_menu(builder.get_object("app-menu"))


parser = argparse.ArgumentParser()
parser.add_argument("--questions", help="which sub questions should be graded", default='questions.txt')
parser.add_argument("--students", help="which students should be graded", default='students.txt')
parser.add_argument("--grades", help="where to store the grades (filename)", default='grades.txt')
args = parser.parse_args()

app = MyApplication()
app.set_input_files(args.questions, args.students, args.grades)
exit_status = app.run()
sys.exit(exit_status)

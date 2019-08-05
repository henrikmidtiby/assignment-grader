import re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
from DebugDecorator import debug


class ListOfReasonsWidget(Gtk.TextView):
    __gsignals__ = {
        'reason_selected': (GObject.SIGNAL_RUN_FIRST, None,
                      (int, str))
    }

    def __init__(self) -> None:
        Gtk.TextView.__init__(self)
        self.list_of_reasons_buffer = Gtk.TextBuffer()
        self.set_editable(False)
        self.set_cursor_visible(False)
        self.set_can_focus(False)
        self.set_buffer(self.list_of_reasons_buffer)
        self.list_of_reasons_buffer.set_text('')
        self.reason_tag = self.list_of_reasons_buffer.create_tag('reason_tag')
        self.reason_tag.connect('event', self.click_in_list_of_reasons)

    def click_in_list_of_reasons(self, tag, widget, event, iter):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            clicked_reason = self.get_content_of_reason_tag_indicated_by_iter(iter)
            point, reason = self.interpret_clicked_reason(clicked_reason)
            self.emit('reason_selected', point, reason)
            return True

    def get_content_of_reason_tag_indicated_by_iter(self, iter):
        end_iter = iter.copy()
        end_iter.forward_to_tag_toggle(self.reason_tag)
        iter.backward_to_tag_toggle(self.reason_tag)
        clicked_reason = self.list_of_reasons_buffer.get_text(iter, end_iter, False)
        return clicked_reason

    def interpret_clicked_reason(self, clicked_reason: str):
        pattern = re.compile('\s*(\d+) \(\d+\) - (.*)')
        res = pattern.match(clicked_reason)
        if res:
            point = int(res.group(1))
            reason = res.group(2)
            return point, reason

    def update_list_of_reasons(self, question: str, question_description: str, point, partial_grade_handler):
        """
        Is called when the list of reasons for a certain sub evaluation should be updated.
        Then the description of the question is inserted on the first line and the
        earlier used descriptions are inserted below.
        """
        self.list_of_reasons_buffer.set_text("%s\n" % question_description)
        if point is None:
            self.show_add_given_reasons_for_this_question(partial_grade_handler, question)
        else:
            self.show_given_reasons_close_to_the_score(partial_grade_handler, point, question)

    def show_add_given_reasons_for_this_question(self, partial_grade_handler, question: str):
        point_keys = partial_grade_handler.dict_of_reasons[question].keys()
        for point_key in sorted(point_keys, key=lambda temp: int('%s0' % temp)):
            self.given_point_insert_all_matching_reasons(point_key, question, partial_grade_handler)

    def show_given_reasons_close_to_the_score(self, partial_grade_handler, point: int, question: str):
        self.given_point_insert_all_matching_reasons(point - 1, question, partial_grade_handler)
        self.given_point_insert_all_matching_reasons(point, question, partial_grade_handler)
        self.given_point_insert_all_matching_reasons(point + 1, question, partial_grade_handler)

    def given_point_insert_all_matching_reasons(self, point, question: str, partial_grade_handler):
        for reason_key in partial_grade_handler.dict_of_reasons[question][str(point)].keys():
            self.insert_point_and_reason_in_list(question, point, reason_key, partial_grade_handler)

    def insert_point_and_reason_in_list(self, question: str, point, reason: str, partial_grade_handler):
        multiplicity = partial_grade_handler.dict_of_reasons[question][str(point)][reason]
        end_iter = self.list_of_reasons_buffer.get_end_iter()
        new_reason = "%2s (%s) - %s" % (point, multiplicity, reason)
        self.list_of_reasons_buffer.insert_with_tags(end_iter, new_reason, self.reason_tag)
        self.list_of_reasons_buffer.insert(end_iter, "\n")

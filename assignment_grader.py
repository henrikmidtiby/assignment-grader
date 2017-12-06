import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


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
            label = Gtk.Label("Q%d" % k)
            label.set_max_width_chars(entry_label_min_width)
            point = Gtk.Entry()
            point.connect("changed", self.points_has_changed, k)
            point.set_width_chars(entry_point_min_width)
            reason = Gtk.Entry()
            reason.set_width_chars(entry_reason_min_width)
            self.grid.attach(label, 0, k, 1, 1)
            self.grid.attach(point, 1, k, 1, 1)
            self.grid.attach(reason, 2, k, 1, 1)
            self.grid_labels.append(label)
            self.grid_points.append(point)
            self.grid_reasons.append(reason)

        self.h_box.pack_start(self.grid, True, True, 0)

        self.list_of_reasons = Gtk.TextView()
        self.list_of_reasons.get_buffer().set_text('This is a test.\nSeveral lines...')
        self.h_box.pack_start(self.list_of_reasons, True, True, 0)

    def points_has_changed(self, widget, k):
        self.grid_reasons[k - 1].set_text('asdf')

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
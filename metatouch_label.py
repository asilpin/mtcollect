from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QCursor, QPalette, QFont

class ClassLabelWidget(QtWidgets.QWidget):

    def __init__(self, LABELS):
        QtWidgets.QWidget.__init__(self)

        self.LabelVL = QtWidgets.QVBoxLayout()
        self.setLayout(self.LabelVL)
        self.setFixedHeight(175)
        
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Minimum
        )
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: rgb(44, 44, 46); border-radius: 8px;')

        self.title = QtWidgets.QLabel('Class Labels')
        self.title.setStyleSheet("color: white; font: bold")
        self.LabelVL.addWidget(self.title)

        self.scroll = QScrollArea(self)
        self.LabelVL.addWidget(self.scroll)
        self.scroll.setWidgetResizable(True)
        self.scrollContent = QWidget(self.scroll)
        self.scrollVL = QtWidgets.QVBoxLayout(self.scrollContent)
        self.scrollContent.setLayout(self.scrollVL)
        self.scroll.ensureWidgetVisible(self.scrollContent)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.horizontalScrollBar().setEnabled(False)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.labels = []
        self.frames_collected = []
        self.label_raw_text = LABELS
        self.selected_color = "color: rgb(255, 69, 58)"
        self.default_color = "color: white"
        self.palette = QPalette()
        self.font = QFont()

        for i in range(0, len(self.label_raw_text)):

            # initialize each label
            curr_label = QtWidgets.QLabel()
            curr_label.setText(str(i))

            # set first label to selected
            if i == 0:
                curr_label.setStyleSheet(self.selected_color)
            else:
                curr_label.setStyleSheet(self.default_color)

            # add label to layout
            self.scrollVL.addWidget(curr_label)

            self.labels.append(curr_label)
            self.frames_collected.append(0)
            self.resize(curr_label.sizeHint())

        self.scroll.setWidget(self.scrollContent)
        self.set_label_text()

    def get_current_label_raw_text(self):
        """Returns selected label."""
        for i in range(0, len(self.labels)):
            if self.labels[i].styleSheet() == self.selected_color:
                return self.label_raw_text[i]

    def get_current_label_index(self):
        """Returns index of selected label."""
        for i in range(0, len(self.labels)):
            if self.labels[i].styleSheet() == self.selected_color:
                return i

    def get_current_frames(self):
        """Returns number of frames collected for selected label."""
        for i in range(0, len(self.labels)):
            if self.labels[i].styleSheet() == self.selected_color:
                return self.frames_collected[i]

    def add_frames_current_label(self, num_frames):
        """Adds num_frames to label's frame count."""
        current_index = self.get_current_label_index()

        self.frames_collected[current_index] += num_frames

        # minimum frames collected is 0
        if self.frames_collected[current_index] < 0:
            self.frames_collected[current_index] = 0

        # update label text
        self.set_label_text()

    def set_label_text(self):
        """Set label text to label and frame count."""
        for label, frame_count, label_raw_text in zip(self.labels,
                                                      self.frames_collected,
                                                      self.label_raw_text):

            label_text = "{} ({} frames)".format(label_raw_text, frame_count)
            label.setText(label_text)

    def move_down(self):
        """Moves selected label to one below."""
        curr_ind = self.get_current_label_index()
        if curr_ind < len(self.labels)-1 and curr_ind+1 < len(self.labels):
            # changes colors of labels to highlight the currently selected one
            self.labels[curr_ind].setStyleSheet(self.default_color)
            self.labels[curr_ind+1].setStyleSheet(self.selected_color)

    def move_up(self):
        """Moves selected label to one below."""
        curr_ind = self.get_current_label_index()
        if curr_ind > 0 and curr_ind-1 >= 0:
            # changes colors of labels to highlight the currently selected one
            self.labels[curr_ind].setStyleSheet(self.default_color)
            self.labels[curr_ind-1].setStyleSheet(self.selected_color)

    def switch_theme(self, palette):
        self.palette = palette
        curr_index = self.get_current_label_index()
        self.title.setStyleSheet(self.default_color)
        for i in range(len(self.labels)):
            if i == curr_index:
                self.labels[i].setStyleSheet(self.selected_color)
            else:
                self.labels[i].setStyleSheet(self.default_color)

    def setFont(self, font):
        self.font = font
        for i in range(len(self.labels)):
            self.labels[i].setFont(font)
        font_bold = QFont(font)
        font_bold.setWeight(99)
        self.title.setFont(font_bold)

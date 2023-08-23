from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont

class ClassLabelWidget(QtWidgets.QWidget):

    def __init__(self, LABELS):
        QtWidgets.QWidget.__init__(self)
        self.font_family = 'Verdana'
        self.fontsize_normal = 11

        self.LabelVL = QtWidgets.QVBoxLayout()
        self.setLayout(self.LabelVL)
        self.setFixedHeight(175)
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: rgb(44, 44, 46); border-radius: 8px;')

        self.title = QtWidgets.QLabel('Class Labels')
        self.LabelVL.addWidget(self.title)

        self.scroll = QtWidgets.QScrollArea()
        self.LabelVL.addWidget(self.scroll)
        self.scrollContent = QtWidgets.QWidget()
        self.scrollVL = QtWidgets.QVBoxLayout()
        self.scrollContent.setLayout(self.scrollVL)
        self.scroll.setWidget(self.scrollContent)
        self.scroll.setWidgetResizable(True)
        self.scroll.ensureWidgetVisible(self.scrollContent)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.horizontalScrollBar().setEnabled(False)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.labels = []
        self.frames_collected = []
        self.label_raw_text = LABELS
        self.selected_color = "color: rgb(255, 69, 58)"
        self.default_color = "color: white"
        self.font = QFont(self.font_family,self.fontsize_normal)

        self.maxWidth = 0
        for i in range(0, len(self.label_raw_text)):

            # initialize each label
            curr_label = QtWidgets.QLabel()
            curr_label.setText(str(i))
            if curr_label.width() > self.maxWidth:
                self.maxWidth = curr_label.width()

            # add label to layout
            self.scrollVL.addWidget(curr_label)

            self.labels.append(curr_label)
            self.frames_collected.append(0)

        self.setMinimumWidth(self.maxWidth)
        self.set_label_text()
        self.set_appearance()

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

    def set_appearance(self):
        self.title.setFont(self.font)
        self.title.setStyleSheet("color: white; font: bold")
        for i in range(len(self.labels)):
            self.labels[i].setFont(self.font)
            self.labels[i].setStyleSheet("color: white")
        self.labels[0].setStyleSheet(self.selected_color)

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

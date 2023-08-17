#!/usr/bin/env python3
# ==============================================================================
"""
	__	___		__		 ______					__	
   /  |/  /__  / /_____ /_	__/___	__	_______/ /_ 
  / /|_/ / _ \/ __/ __ `// / / __ \/ / / / ___/ __ \
 / /  / /  __/ /_/ /_/ // / / /_/ / /_/ / /__/ / / /
/_/  /_/\___/\__/\__,_//_/	\____/\__,_/\___/_/ /_/  V.0.1

Author: Abhipol Vibhatasilpin (abhipol@umich.edu)
Description:

"""
# ==============================================================================

# System
import sys
import os
import time
import configparser
import subprocess

# Data processing
import numpy as np
from scipy.ndimage import rotate

# UI tools 
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtCore  import *
from PyQt5.QtGui   import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor
import pyqtgraph as pg

# Custom 

# ==============================================================================
# Read in configuration
config = configparser.ConfigParser()
config.read('config.ini')

CHANNELS = config['GLOBAL']['CHANNELS'][1:-1].split(', ') 
NUM_CHANNELS = len(CHANNELS) 
FRAMELENGTH = int(config['GLOBAL']['FRAMELENGTH'])
LABELS = config['GLOBAL']['LABELS'][1:-1].split(', ') 

# ==============================================================================

# Global font configuration
font_family = 'Verdana'
fontsize_normal = 11

class MetaTouch(QtWidgets.QMainWindow):
	""" Driver class for the application """
	def __init__(self):
		super(MetaTouch, self).__init__()
		uic.loadUi("mtplot_win_layout.ui", self)
		self.show()
		
		self.setWindowTitle("MetaTouch Plotter V.0.1")
		
		# Initialize pg object containers
		self.title_labels = []
		self.lineplots = []
		self.spectrograms = []
		self.update_signals = []

		# Set up the FPS counter
		self.num_frames = 0
		self.fps_label = QtWidgets.QLabel()
		self.fps_label.setText("FPS: {}".format(self.num_frames))

		# Set up the message label at the bottom
		self.footer = QtWidgets.QLabel("MetaTouch")
		self.footer.setWordWrap(True)
		self.footer.setFixedWidth(self.width())
		self.footer.setAlignment(Qt.AlignHCenter)

		self.build()

	def build(self):
		""" Called after class constructor """
		self.LinePane = QtWidgets.QWidget()
		self.LinePaneHL = QtWidgets.QHBoxLayout()
		self.SpecPane = QtWidgets.QWidget()
		self.SpecPaneHL = QtWidgets.QHBoxLayout()
		self.LinePane.setLayout(self.LinePaneHL)
		self.SpecPane.setLayout(self.SpecPaneHL)
		
		# Set up the spectrograms and line plots
		for i in range(NUM_CHANNELS):
			lineplot_with_label = QtWidgets.QWidget()
			lineplot_with_label_VL = QtWidgets.QVBoxLayout()
			lineplot_with_label.setLayout(lineplot_with_label_VL)
			
			title = QtWidgets.QLabel(self)
			title.setContentsMargins(20,0,0,0)
			title.setFont(QtGui.QFont(font_family, fontsize_normal))
			title.setText(CHANNELS[i])
			self.title_labels.append(title)

			lineplot = LineplotWidget()
			lineplot.setMinimumHeight(0)
			lineplot.read_collected.connect(lineplot.update)
			
			self.update_signals.append(lineplot.read_collected)
			self.lineplots.append(lineplot)

			lineplot_with_label_VL.addWidget(title, alignment=Qt.AlignCenter)
			lineplot_with_label_VL.addWidget(lineplot)

			self.LinePaneHL.addWidget(lineplot_with_label)

			spectrogram = SpectrogramWidget()
			spectrogram.read_collected.connect(spectrogram.update)
			
			self.update_signals.append(spectrogram.read_collected)
			self.spectrograms.append(spectrogram)

			self.SpecPaneHL.addWidget(spectrogram)
		
		# Set up the main display
		self.PlotVL.addWidget(self.LinePane)
		self.PlotVL.addWidget(self.SpecPane)
		# Set up the bottom console widgets
		self.FooterGL.addWidget(self.footer, 1, 1, 
								 alignment=Qt.AlignHCenter)
		self.FooterGL.addWidget(self.fps_label, 1, 1, 
								 alignment=Qt.AlignRight)
		
		self.ds = DataSource(self.update_signals, NUM_CHANNELS)
	
		# Set up timer(s)
		self.plot_timer = QtCore.QTimer()
		self.plot_timer.timeout.connect(self.ds.read_channels)
		self.plot_timer.start(100)
		
		# Apply theme
		self.set_theme()

	def keyPressEvent(self, event):
		"""Listen and handle keyboard input."""

		# SpaceBar
		if event.key()==Qt.Key_Space:
			self.footer.setText("Collecting...")
			# self.on_spacebar()
			# self.stepsbar.update_label_state(self.labels)
		# L
		elif event.key()==Qt.Key_L:
			self.footer.setText("Loading...")
			# self.stepsbar.set_state(0, 1)
			# self.on_load()
		# S
		elif event.key()==Qt.Key_S:
			self.footer.setText("Saving...")
			# self.stepsbar.set_state(2, 1)
			# self.on_save()
		# P
		elif event.key()==Qt.Key_P:
			self.footer.setText("Printed to [filename]")
			# self.stepsbar.set_state(2, 1)
			# self.on_save()
		# BackSpace
		elif event.key()==Qt.Key_Backspace:
			self.footer.setText("Deleting...")
			# self.on_delete_frame()
			# self.stepsbar.update_label_state(self.labels)
		# Key Up
		elif event.key()==Qt.Key_Up:
			self.footer.setText("Up")
			# self.on_up()
		# Key Down
		elif event.key()==Qt.Key_Down:
			self.footer.setText("Down")
			# self.on_down()
		# Key Left
		elif event.key()==Qt.Key_Left:
			self.footer.setText("Left")
			# self.on_up()
		# Key Right
		elif event.key()==Qt.Key_Right:
			self.footer.setText("Right")
			# self.on_right()
		else:
			self.footer.setText("Invalid Keyboard Input.")

	def set_theme(self):
		palette = QPalette()
		palette.setColor(QPalette.Window, QColor(10, 10, 10))
		palette.setColor(QPalette.WindowText, Qt.white)
		palette.setColor(QPalette.Base, Qt.black)
		palette.setColor(QPalette.AlternateBase, Qt.gray)
		palette.setColor(QPalette.ToolTipBase, Qt.white)
		palette.setColor(QPalette.ToolTipText, Qt.white)
		palette.setColor(QPalette.Text, Qt.white)
		palette.setColor(QPalette.Button, Qt.black)
		palette.setColor(QPalette.Background, QColor(28, 28, 30))
		palette.setColor(QPalette.ButtonText, Qt.white)
		palette.setColor(QPalette.BrightText, Qt.red)
		palette.setColor(QPalette.Link, QColor(42, 130, 218))
		palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
		palette.setColor(QPalette.HighlightedText, Qt.black)
		self.setPalette(palette)

		board_stylesheet = 'background-color: rgb(44, 44, 46); border-radius: 8px'
		self.LinePane.setAttribute(QtCore.Qt.WA_StyledBackground, True)
		self.LinePane.setStyleSheet(board_stylesheet)
		self.SpecPane.setAttribute(QtCore.Qt.WA_StyledBackground, True)
		self.SpecPane.setStyleSheet(board_stylesheet)

		for spectrogram in self.spectrograms:
			spectrogram.setBackground((44, 44, 46))
		for lineplot in self.lineplots:
			lineplot.setBackground((44, 44, 46))
		for i in range(NUM_CHANNELS):
			self.title_labels[i].setStyleSheet("color: white; font: bold")

class DataSource():
	""" Class that handles incoming data """ 
	def __init__(self, event, channel):
		self.signal = event
		self.channel = channel
		gradient_slice = np.linspace(0,2,1000)
		self.slice = np.tile(gradient_slice, (channel, 1))

	def read_channels(self):
		for i in range(self.channel):
			self.signal[2*i].emit(self.slice[i])
			self.signal[2*i + 1].emit(self.slice[i])

class SpectrogramWidget(pg.PlotWidget):
	read_collected = QtCore.pyqtSignal(np.ndarray)

	def __init__(self):
		super(SpectrogramWidget, self).__init__()

		self.img = pg.ImageItem()
		self.addItem(self.img)

		self.img_array = np.zeros((100, 1000))
		cmap = pg.colormap.get('magma')

		self.img.setColorMap(colorMap=cmap)

		self.setXRange(0,1000)
		self.setYRange(0,100)
		self.setLabel('left', 'Frame')
		self.setLabel('bottom', 'Index')
		self.setMouseEnabled(x=False,y=False)
		# self.addColorBar(self.img,colorMap='magma',
		#				  interactive=False,
		#				  values=(0,2))
		self.setMenuEnabled(enableMenu=False)
		self.show()

	def update(self, layer):
		self.img_array = np.roll(self.img_array, -1, 0)
		self.img_array[-1:] = layer
		img_display = np.flip(self.img_array, axis=1)
		img_display = rotate(img_display,angle=90)
		self.img.setImage(img_display)

class LineplotWidget(pg.PlotWidget):
	read_collected = QtCore.pyqtSignal(np.ndarray)
	def __init__(self):
		super(LineplotWidget, self).__init__()
		self.line = pg.PlotDataItem(np.zeros(1000))
		self.addItem(self.line)
		self.setLabel('left', 'Voltage', units='mV')
		self.setLabel('bottom', 'Index')
		self.setMouseEnabled(x=False,y=False)
		self.setMenuEnabled(enableMenu=False)
		self.show()

	def update(self, layer):
		self.line.setData(layer)

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	win = MetaTouch()
	app.setStyle("Fusion")
	app.setFont(QtGui.QFont(font_family, fontsize_normal))
	app.exec()	  



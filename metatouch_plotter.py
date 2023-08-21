#!/usr/bin/env python3
# ==============================================================================
"""
	__	___		__		 ______					__	
   /  |/  /__  / /_____ /_	__/___	__	_______/ /_ 
  / /|_/ / _ \/ __/ __ `// / / __ \/ / / / ___/ __ \
 / /  / /  __/ /_/ /_/ // / / /_/ / /_/ / /__/ / / /
/_/  /_/\___/\__/\__,_//_/	\____/\__,_/\___/_/ /_/  V.0.1

Author: Abhipol Vibhatasilpin (abhipol@umich.edu)
Description: Configurable data visualization and collection tool for the 
			 MetaTouch research project

"""
# ==============================================================================

# System
import sys
import os
import time
import configparser
import subprocess
from datetime import datetime

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
from metatouch_label import ClassLabelWidget

# ==============================================================================
# Read in configuration
config = configparser.ConfigParser()
config.read('config.ini')

CHANNELS = config['GLOBAL']['CHANNELS'][1:-1].split(', ') 
NUM_CHANNELS = len(CHANNELS) 
CLASSES = config['GLOBAL']['CLASSES'][1:-1].split(', ') 
CAPTURE_SIZE = int(config['GLOBAL']['CAPTURE_SIZE'])
FRAME_LENGTH = int(config['GLOBAL']['FRAME_LENGTH'])
INDEX_WIDTH = int(config['GLOBAL']['INDEX_WIDTH'])

# ==============================================================================

# Global font configuration
font_family = 'Verdana'
fontsize_normal = 11
fontsize_maximized = 14
fontsize_labels = fontsize_normal
fontsize_footer = fontsize_normal + 8

class MetaTouch(QtWidgets.QMainWindow):
	""" Driver class for the application """
	def __init__(self):
		super(MetaTouch, self).__init__()
		uic.loadUi("metatouch_layout.ui", self)
		self.show()
		self.setWindowTitle("MetaTouch Plotter V.0.1")
		
		# Keep track of plot elemenets
		self.title_labels = []
		self.lineplots = []
		self.spectrograms = []
		self.update_signals = []

		self.labels = ClassLabelWidget(CLASSES)	
		
		# Set up the FPS counter
		self.num_frames = 0
		self.fps_label = QtWidgets.QLabel()
		self.fps_label.setText("FPS: {}".format(self.num_frames))

		# Set up the message label at the bottom
		self.footer = QtWidgets.QLabel("MetaTouch")
		self.footer.setWordWrap(True)
		self.footer.setFixedWidth(self.width())
		self.footer.setAlignment(Qt.AlignHCenter)

		# Set up connection status disaply
		self.connection = QtWidgets.QLabel()

		self.build()

	def build(self):
		""" Called after class constructor """

		# Add encapsulating widgets
		self.LinePane = QtWidgets.QWidget()
		self.LinePaneHL = QtWidgets.QHBoxLayout()
		self.SpecArray = QtWidgets.QWidget()
		self.SpecArrayHL = QtWidgets.QHBoxLayout()
		self.SpecPane = QtWidgets.QWidget()
		self.SpecPaneVL = QtWidgets.QVBoxLayout()
		self.PlotPane = QtWidgets.QWidget()
		self.PlotPaneVL = QtWidgets.QVBoxLayout() 
		self.LinePane.setLayout(self.LinePaneHL)
		self.SpecArray.setLayout(self.SpecArrayHL)
		self.SpecPane.setLayout(self.SpecPaneVL)
		self.PlotPane.setLayout(self.PlotPaneVL)

		# Enforce global pyqtgraph configuration
		pg.setConfigOption('background', (44, 44, 46))
		
		# Set up the spectrograms and line plots
		for i in range(NUM_CHANNELS):
			
			# Create a temp widget that holds lineplot and label
			lineplot_with_label = QtWidgets.QWidget()
			lineplot_with_label_VL = QtWidgets.QVBoxLayout()
			lineplot_with_label.setLayout(lineplot_with_label_VL)
		
			# Generate a label for the plot title	
			title = QtWidgets.QLabel(self)
			title.setText(CHANNELS[i])

			self.title_labels.append(title)

			# Instantiate a line plot widget and route the signal
			lineplot = LineplotWidget()
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

			self.SpecArrayHL.addWidget(spectrogram)
		
		# Create a colorbar widget
		self.SpecBar = pg.GraphicsLayoutWidget()
		self.Cbar = pg.ColorBarItem(values=(0,2),
								width=6,
								colorMap='magma',
								interactive=False,
								orientation='horizontal')
		self.SpecBar.addItem(self.Cbar)

		# Assemble the spectogram pane		
		self.SpecPaneVL.addWidget(self.SpecArray)
		self.SpecPaneVL.addWidget(self.SpecBar)

		# Set up the main display
		self.PlotPaneVL.addWidget(self.LinePane, 3)
		self.PlotPaneVL.addWidget(self.SpecPane, 7)
		self.PlotVL.addWidget(self.PlotPane)
		
		# Set up the console widgets
		self.ConsoleGL.addWidget(self.labels, 1, 1,alignment = Qt.AlignLeft)

		# Set up the footer widgets
		self.FooterGL.addWidget(self.footer, 1, 1, 
								 alignment=Qt.AlignHCenter)
		self.FooterGL.addWidget(self.fps_label, 1, 1, 
								 alignment=Qt.AlignRight)
		
		self.ds = DataSource(self.update_signals)
	
		# Set up timer(s)
		self.plot_timer = QtCore.QTimer()
		self.plot_timer.timeout.connect(self.ds.read_channels)
		self.plot_timer.start(100)
		
		# Apply theme
		self.set_appearance()

	def keyPressEvent(self, event):
		"""Listen and handle keyboard input."""
		self.footer.setText("MetaTouch")
		# Q
		if event.key()==Qt.Key_Q:
			quit()
		# SpaceBar
		if event.key()==Qt.Key_Space:
			self.footer.setText("Collecting...")
			self.on_spacebar()
		# L
		elif event.key()==Qt.Key_L:
			self.footer.setText("Loading...")
			self.on_load()
		# S
		elif event.key()==Qt.Key_S:
			self.footer.setText("Saving...")
			self.on_save()
		# BackSpace
		elif event.key()==Qt.Key_Backspace:
			self.footer.setText("Deleting...")
			self.on_delete_frame()
		# P
		elif event.key()==Qt.Key_P:
			self.on_print()
		# Key Up
		elif event.key()==Qt.Key_Up:
			self.on_up()
		# Key Down
		elif event.key()==Qt.Key_Down:
			self.on_down()
		# Key Left
		elif event.key()==Qt.Key_Left:
			self.on_up()
		# Key Right
		elif event.key()==Qt.Key_Right:
			self.on_right()
		else:
			self.footer.setText("Invalid Keyboard Input.")
	
	def on_print(self):
		screenshot = self.PlotPane.grab(self.PlotPane.rect())
		filename = datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S") 
		screenshot.save(filename + ".png")
		self.footer.setText("Printed to " + filename)
	
	def on_up(self):
		self.labels.move_up()
	
	def on_down(self):
		self.labels.move_down()

	def on_spacebar(self):
		"""Collect frames."""
		self.footer.setText("Collecting "+str(CAPTURE_SIZE)+" frames.")
		current_label = self.labels.get_current_label_raw_text()
		current_label = current_label.lower().strip().replace(" ", "_")
		num_frame = self.labels.get_current_frames()
		filename = 'training_data_{}_{}.npy'.format(current_label,num_frame)
		collected_data = np.empty((NUM_CHANNELS, CAPTURE_SIZE, INDEX_WIDTH)) 
		for i in range(NUM_CHANNELS):
			collected_data[i] = self.spectrograms[i].img_array[-CAPTURE_SIZE:]
		print(np.shape(collected_data))
		np.save(filename, collected_data)
		self.labels.add_frames_current_label(CAPTURE_SIZE)
		self.footer.setText("Done Collecting Frames.")

	def set_appearance(self):
		self.centralwidget.setContentsMargins(20, 10, 20, 10)
		self.SpecBar.setMaximumHeight(50)

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

		self.footer.setFont(QFont(font_family, fontsize_footer))
		
		for title in self.title_labels:
			title.setContentsMargins(20,0,0,0)
			title.setFont(QFont(font_family, fontsize_normal))
			title.setStyleSheet("color: white; font: bold")
		for spectrogram in self.spectrograms:
			spectrogram.setBackground((44, 44, 46))
		for lineplot in self.lineplots:
			lineplot.setBackground((44, 44, 46))

class DataSource():
	""" Class that handles incoming data """ 
	def __init__(self, event):
		self.signal = event
		self.slice = np.random.uniform(0,2,size=(NUM_CHANNELS,INDEX_WIDTH))
		# gradient_slice = np.linspace(0,2,INDEX_WIDTH)
		# self.slice = np.tile(gradient_slice, (channel, 1))

	def read_channels(self):
		self.slice = np.random.uniform(0,2,size=(NUM_CHANNELS,INDEX_WIDTH))
		for i in range(NUM_CHANNELS):
			self.signal[2*i].emit(self.slice[i])
			self.signal[2*i + 1].emit(self.slice[i])

class SpectrogramWidget(pg.PlotWidget):
	read_collected = QtCore.pyqtSignal(np.ndarray)

	def __init__(self):
		super(SpectrogramWidget, self).__init__()

		self.img = pg.ImageItem()
		self.addItem(self.img)

		self.img_array = np.zeros((FRAME_LENGTH, INDEX_WIDTH))
		cmap = pg.colormap.get('magma')

		self.img.setColorMap(colorMap=cmap)

		self.setXRange(0,INDEX_WIDTH)
		self.setYRange(0,FRAME_LENGTH)
		self.setLabel('left', 'Frame')
		self.setLabel('bottom', 'Index')
		self.setMouseEnabled(x=False,y=False)
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
		self.line = pg.PlotDataItem(np.zeros(INDEX_WIDTH))
		self.line.setPen(width=3)
		self.addItem(self.line)
		self.setLabel('left', 'Voltage', units='V')
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
	app.setFont(QFont(font_family, fontsize_normal))
	app.exec()	  



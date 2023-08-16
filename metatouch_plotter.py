#!/usr/bin/env python3
# ==============================================================================
"""
    __  ___     __       ______                 __  
   /  |/  /__  / /_____ /_  __/___  __  _______/ /_ 
  / /|_/ / _ \/ __/ __ `// / / __ \/ / / / ___/ __ \
 / /  / /  __/ /_/ /_/ // / / /_/ / /_/ / /__/ / / /
/_/  /_/\___/\__/\__,_//_/  \____/\__,_/\___/_/ /_/  V.0.1

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
import pyqtgraph as pg

# Custom 

# ==============================================================================
# Read in configuration
config = configparser.ConfigParser()
config.read('config.ini')

CHANNELS = config['GLOBAL']['CHANNELS'][1:-1].split(', ') 
NUM_CHANNELS = len(CHANNELS) 

# ==============================================================================

class MetaTouch(QtWidgets.QMainWindow):
    """ Driver class for the application """
    def __init__(self):
        super(MetaTouch, self).__init__()
        uic.loadUi("mtplot_win_layout.ui, self)
        self.show()
        
        self.setWindowTitles("MetaTouch Plotter V.0.1")
        self.spectograms = []
        self.lineplots = []

        # Set up the FPS counter
        self.num_frames = 0
        self.fps_label = QtWidget.QLabel()
        self.fps_label.setText("FPS: {}".format(self.num_frames))

        # Set up the message label at the bottom
        self.footer = QtWidgets.QLabel("MetaTouch")
        self.footer.setWordWrap(True)
        self.footer.setFixedWidth(self.width())
        self.footer.setAlignment(Qt.AlignHCenter)

        self.build()

    def build(self):
        """ Called after class constructor """
        # Set up the spectograms and line plots
        for i in range(NUM_CHANNELS):
            

        w1 = SpectrogramWidget()
        w1.read_collected.connect(w1.update)

        w2 = SpectrogramWidget()
        w2.read_collected.connect(w2.update)

        w3 = SpectrogramWidget()
        w3.read_collected.connect(w3.update)

        w4 = SpectrogramWidget()
        w4.read_collected.connect(w4.update)

        w5 = LineplotWidget()
        w5.setTitle("40KHz Phase")
        w1.read_collected.connect(w5.update)

        w6 = LineplotWidget()
        w6.setTitle("40KHz Mag")
        w2.read_collected.connect(w6.update)

        w7 = LineplotWidget()
        w7.setTitle("200KHz Mag")
        w3.read_collected.connect(w7.update)

        w8 = LineplotWidget()
        w8.setTitle("200KHz Phase")
        w4.read_collected.connect(w8.update)

        # Set up the bottom console widgets
        self.consoleGL.addWidget(self.footer, 1, 1, alignment=QtCore.Qt.AlignHCenter)
        self.consoleGL.addWidget(self.fps_label, 1, 1, alignment=QtCore.QtAlignRight)

        d = DataStream(event=[w1.read_collected,
                              w2.read_collected,
                              w3.read_collected,
                              w4.read_collected],channel=4)
    
        # Setup timer(s)
        t = QtCore.QTimer()
        t.timeout.connect(d.read_channels)
        t.start(1)

    def keyPressEvent(self, event):
        """Listen to and service keyboard input signal"""

class DataSource():
    def __init__(self, event, channel):
        self.signal = event
        self.channel = channel
        self.slice = np.zeros((channel, 1000))

    def read_channels(self):
        self.generate_data()
        for i in range(self.channel):
            dataframe = self.slice[i]
            self.signal[i].emit(dataframe)

    def generate_data(self):
        self.slice = np.random.randint(0,100,(self.channel,1000))

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
        self.addColorBar(self.img,colorMap='magma',
                         interactive=False,
                         values=(0,2))
        self.setMenuEnabled(enableMenu=False)
        self.show()

    def update(self, layer):
        self.img_array = np.roll(self.img_array, -1, 0)
        self.img_array[-1:] = layer
        rotate(input=self.img_array,angle=90)
        np.fliplr(self.img_array)

class LineplotWidget(pg.PlotWidget):
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

sys.exit(app.exec())    



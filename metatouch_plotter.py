import sys
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import socket
from threading import Thread
from scipy.ndimage import rotate

HOST = "192.168.0.239"
PORT = 9090

class DataStream():
    def __init__(self, _host, _port, event):
        self.host =  _host
        self.port = _port
        self.signal = event
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.slice = np.zeros((4, 1000))

    def read_channels(self):
        for i in range(self.slice.shape[0]):
            dataframe = self.slice[i]
            self.signal[i].emit(dataframe)

    def thread(self):
        return Thread(target=self.stream)

    def run_connection(self, conn, index):
        conn.settimeout(3)
        while True:
            try:          
                signal = np.array([])
                bytes_received = 0
                while(bytes_received < 2 * 4008):
                    message = conn.recv(2 * 4008 - bytes_received)
                    temp = np.frombuffer(message, dtype=np.uint8)
                    signal = np.hstack((signal, temp))
                    bytes_received += temp.shape[0]
                signal = np.asarray(signal, dtype='<B').view(np.uint16)
                self.slice = np.reshape(signal, (4, 1002))[:,:-2].astype(np.float32)
                
            except socket.timeout:
                self.s.settimeout(10)
                print("timeout")
                self.slice = np.zeros((4, 1000))
                return index
        
    def stream(self):
        self.s.bind((self.host, self.port))
        self.s.listen(5) 
        self.s.setblocking(0)
        self.s.settimeout(20)
        index = 0
        while True:
            try:
                conn, addr = self.s.accept()
                print(f"Connected to {addr}")
                index = self.run_connection(conn, index)
            except socket.timeout:
                print("Ended Connection")
                np.zeros((4, 1000))
                exit()

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
        self.setLabel('bottom', 'Time', units='ms')
        self.setMouseEnabled(x=False,y=False)
        self.addColorBar(self.img,colorMap='magma',interactive=False,values=(0,2))
        self.setMenuEnabled(enableMenu=False)
        self.show()

    def update(self, layer):
        self.img_array = np.roll(self.img_array, -1, 0)
        self.img_array[-1:] = layer
        self.img.setImage(rotate(self.img_array,angle=270))

class LineplotWidget(pg.PlotWidget):
    def __init__(self):
        super(LineplotWidget, self).__init__()
        self.line = pg.PlotDataItem(np.zeros(1000))
        self.addItem(self.line)
        self.setLabel('left', 'Voltage', units='mV')
        self.setLabel('bottom', 'Frame')
        self.setMouseEnabled(x=False,y=False)
        self.setMenuEnabled(enableMenu=False)
        self.show()

    def update(self, layer):
        self.line.setData(layer)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    central_widget = QtWidgets.QWidget()
    layout = QtWidgets.QGridLayout()
    central_widget.setLayout(layout)

    w1 = SpectrogramWidget()
    w1.setTitle("40KHz Phase")
    w1.read_collected.connect(w1.update)

    w2 = SpectrogramWidget()
    w2.setTitle("40KHz Mag")
    w2.read_collected.connect(w2.update)

    w3 = SpectrogramWidget()
    w3.setTitle("200KHz Mag")
    w3.read_collected.connect(w3.update)

    w4 = SpectrogramWidget()
    w4.setTitle("200KHz Phase")
    w4.read_collected.connect(w4.update)

    # w5 = LineplotWidget()
    # w1.read_collected.connect(w5.update)

    # w6 = LineplotWidget()
    # w2.read_collected.connect(w6.update)

    # w7 = LineplotWidget()
    # w3.read_collected.connect(w7.update)

    # w8 = LineplotWidget()
    # w4.read_collected.connect(w8.update)

    layout.addWidget(w1, 0, 0)
    layout.addWidget(w2, 0, 1)
    layout.addWidget(w3, 0, 2)
    layout.addWidget(w4, 0, 3)
    # layout.addWidget(w5, 1, 0)
    # layout.addWidget(w6, 1, 1)
    # layout.addWidget(w7, 1, 2)
    # layout.addWidget(w8, 1, 3)

    d = DataStream(HOST,PORT,
                   [w1.read_collected,w2.read_collected,
                    w3.read_collected,w4.read_collected])
    
    th = d.thread()
    th.start()

    central_widget.show()
    sys.exit(app.exec())  

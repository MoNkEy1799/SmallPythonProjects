import pyqtgraph as pyg
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QPushButton, QWidget, QSlider, QLineEdit, QLabel
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QVector3D, QIntValidator, QFont
import colorsys
import numpy as np

class Main(QMainWindow):
    def __init__(self):
        super().__init__()        
        self.setMinimumSize(400, 400)
        self.resize(2000, 1200)
        self.setWindowTitle("Lorenz Attractor")
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        
        self.trunc = False
        self.widgets1 = list()
        self.widgets2 = list()
        self.plotType = ""
        self.times = 10
        self.currentFadeValue = 0.0
        self.viewAndPlot()
        self.buttonsAndSliders()
        self.changePlotType()
        self.xyz = [(0., 1., 1.05)]
        self.colors = [(1.0, 1.0, 1.0, 1.0)]
        self.ViewWidget.setCameraParams(center=QVector3D(0.052, 0.056, 28.0), elevation=11.0, distance=100, azimuth=-27.0)
        
        self.style = """
        QWidget {background: #19232d}
        QPushButton {background: #455364; border-radius: 5px; color: #e0e1e3}
        QLabel {border: 1px solid #455364; border-radius: 5px; color: #e0e1e3}
        QPushButton::hover {background: #54687a}
        QLineEdit {background: #19232d; border: 1px solid #455364; border-radius: 2px; color: #e0e1e3}
        QSlider::groove::horizontal {background: #455364; height: 5px}
        QSlider::handle:horizontal {background: #9DA9B5; width: 8px; height: 8px; border-radius: 4px; margin: -8px}
        QSlider::handle:hover {background: #346792}
        """

        layout = QGridLayout()
        for i, widget in enumerate(self.widgets1):
            layout.addWidget(widget, 0, i)
            
        for i, widget in enumerate(self.widgets2):
            layout.addWidget(widget, 1, i)
            
        layout.addWidget(self.ViewWidget, 2, 0, 1, layout.columnCount())
        
        wid = QWidget()
        wid.setStyleSheet(self.style)
        wid.setLayout(layout)
        self.setCentralWidget(wid)
        
    @staticmethod    
    def lorenz(xyz, s=10, r=28, b=2.667, dt=0.01):
        x, y, z = xyz
        xDot = s*(y - x)
        yDot = r*x - y - x*z
        zDot = x*y - b*z
        
        return x+xDot*dt, y+yDot*dt, z+zDot*dt
    
    def changePlotType(self):
        if self.plotType == "":
            self.ViewWidget.addItem(self.scatterPlot)
            self.plotType = "scatter"
            return
            
        elif self.plotType == "scatter":
            self.ViewWidget.removeItem(self.scatterPlot)
            self.ViewWidget.addItem(self.linePlot)
            self.plotType = "line"
            
        else:
            self.ViewWidget.removeItem(self.linePlot)
            self.ViewWidget.addItem(self.scatterPlot)
            self.plotType = "scatter"
        
    def viewAndPlot(self):
        viewWidget = gl.GLViewWidget()
        viewWidget.setBackgroundColor("#233153")
        
        scatter = gl.GLScatterPlotItem()
        line = gl.GLLinePlotItem()
        
        self.ViewWidget = viewWidget
        self.scatterPlot = scatter
        self.linePlot = line
        
    def buttonsAndSliders(self):
        size = QSize(90, 30)
        font = QFont("Sans-Serif", 9, QFont.Bold)
        startButton = QPushButton("Start")
        startButton.clicked.connect(lambda: self.timer.start(10))
        startButton.setFixedSize(size)
        startButton.setFont(font)

        stopButton = QPushButton("Stop")
        stopButton.clicked.connect(self.timer.stop)
        stopButton.setFixedSize(size)
        stopButton.setFont(font)
        
        resetButton = QPushButton("Reset")
        resetButton.clicked.connect(self.reset)
        resetButton.setFixedSize(size)
        resetButton.setFont(font)

        changeButton = QPushButton("Plot Type")
        changeButton.clicked.connect(self.changePlotType)
        changeButton.setFixedSize(size)
        changeButton.setFont(font)
              
        timesSlider = QSlider(Qt.Horizontal)
        timesSlider.setMinimum(1)
        timesSlider.setMaximum(100)
        timesSlider.setSliderPosition(10)
        timesSlider.valueChanged.connect(lambda value: setattr(self, "times", value))
        
        truncateButton = QPushButton("Truncate")
        truncateButton.setCheckable(True)
        truncateButton.clicked.connect(lambda state: setattr(self, "trunc", state))
        truncateButton.setFixedSize(size)
        truncateButton.setFont(font)
        
        truncateEdit = QLineEdit()
        validator = QIntValidator()
        validator.setBottom(1)
        truncateEdit.setValidator(validator)
        truncateEdit.setMaxLength(5)
        truncateEdit.setFixedSize(size) 
        truncateEdit.setText("4000")
        truncateEdit.setFont(font)

        speedLabel = QLabel("Speed:")
        speedLabel.setFixedSize(size)
        speedLabel.setFont(font)
        
        self.widgets1.append(startButton)
        self.widgets1.append(stopButton)
        self.widgets1.append(resetButton)
        self.widgets1.append(speedLabel)
        self.widgets1.append(timesSlider)
        self.widgets1.append(changeButton)
        self.widgets1.append(truncateButton)
        self.widgets1.append(truncateEdit)
                
    def reset(self):
        self.xyz = [(0., 1., 1.05)]
        self.colors = [(1.0, 1.0, 1.0, 1.0)]
        self.scatterPlot.setData(pos=self.xyz, size=1, color=np.array(self.colors))
        self.linePlot.setData(pos=self.xyz, width=1, color=np.array(self.colors))
    
    def update(self):
        for _ in range(self.times):
            xNew, yNew, zNew = self.lorenz(self.xyz[-1])
            self.xyz.append((xNew, yNew, zNew))
            
            #self.colorStep(2000)
            self.colorFadeDistance((xNew, yNew, zNew), (0.0, 0.0, 0.0))
            
        self.truncate()
        #self.colorFadeLength(.5, 0.001)
        
        self.scatterPlot.setData(pos=self.xyz, size=2, color=np.array(self.colors))
        self.linePlot.setData(pos=self.xyz, width=1, color=np.array(self.colors))
        
    def colorStep(self, step):
        n = len(self.xyz)%(2*step)
        
        if n <= step:
            c = self.hue2rgb(n/step)
        else:
            c = self.hue2rgb(1.0-n/step)
            
        self.colors.append(c)
        
    def hue2rgb(self, hue):
        return tuple(list(colorsys.hsv_to_rgb(hue, 1.0, 1.0))+[1.0])
    
    def truncate(self):
        if not self.trunc: return
        
        maxLength = int([widget for widget in self.widgets1 if type(widget) == QLineEdit][0].text())
        while len(self.xyz) > maxLength:
            self.xyz.pop(0)
            self.colors.pop(0)
    
    def colorFadeDistance(self, point, origin, pattern=30):
        dist = np.linalg.norm(np.array(origin) - np.array(point))
        hue = dist%pattern/pattern
        self.colors.append(self.hue2rgb(hue))
        
    def colorFadeLength(self, length, speed):
        n = len(self.xyz)
        tail = self.currentFadeValue%1.0
        head = tail + length
        
        if head <= 1.0:
            hue = np.linspace(tail, head, n)
        else:
            first = int((1.0-tail) / length * n)
            second = n - first
            hue = np.append(np.linspace(tail, 1.0, first), np.linspace(0.0, 1.0-head, second))

        self.colors = [self.hue2rgb(h) for h in hue]
        self.currentFadeValue += speed
        
    def run(self):
        self.timer.start(10)
        self.show()


app = QApplication([])
main = Main()
main.run()
app.exec()
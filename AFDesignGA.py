#-------------------------------------------------------------------------------
# Name:AFDesginGA(airFoil Design with Optimizing Methods)
# Purpose:AirFoil Design
#
# Author:      NaotoMORITA
#
# Created:     09/11/2013
# Copyright:   (c) NaotoMORITA 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#-*- coding: utf-8 -*-
import scipy, numpy


import sys, os, random
from PyQt4 import QtGui, QtCore

# Matplotlib Figure object
import matplotlib
import matplotlib.pyplot

# Python Qt4 bindings for GUI objects
import PyQt4.QtGui

# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.backends.backend_qt4agg
import matplotlib.backends.backend_agg

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

class Matplot(matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=3, dpi=50, Fx = numpy.array([[0],[0]]), Fy = numpy.array([[0],[0]])):
        self.Fx = numpy.array(Fx)
        self.Fy = numpy.array(Fy)

        fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)
        self.axes.set_aspect("equal")
        self.axes.set_xlim(0,1)
        self.compute_initial_figure()

        matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)

        matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class FoilPlot(Matplot):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        Matplot.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.filename = "None"
        self.axes.plot(self.Fx, self.Fy)

    def update_figure(self):
        self.load()
        self.axes.plot(self.Fx, self.Fy)
        self.draw()


    def load(self):
        self.filename = QtGui.QFileDialog.getOpenFileName()
        foil = numpy.loadtxt(self.filename,skiprows=1)
        self.Fx = foil[:,0]
        self.Fy = foil[:,1]

class MatPlotWidget(QtGui.QWidget):
    def __init__(self,parent = None):
        QtGui.QWidget.__init__(self, parent = parent)

        self.mpl = FoilPlot()
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.mpl)
        self.setLayout(layout)


class ButtonWidget(QtGui.QWidget):
    def __init__(self,parent = None, Fx = numpy.array([[0],[0]]), Fy = numpy.array([[0],[0]])):
        QtGui.QWidget.__init__(self, parent = parent)
        self.openbutton = QtGui.QPushButton("OPEN Selig-Formated Foil",parent = self)

        layout = QtGui.QGridLayout()
        layout.addWidget(self.openbutton)
        self.setLayout(layout)

class FoilSelectWidget(QtGui.QWidget):
    def __init__(self,parent = None):
        QtGui.QWidget.__init__(self, parent = parent)
        self.selectpanel = QtGui.QWidget()

        self.mpw = MatPlotWidget(parent = self.selectpanel)
        self.foilnamelabel = QtGui.QLabel(parent = self.selectpanel)
        self.foilnamelabel.setText(self.mpw.mpl.filename)
        self.openbutton = ButtonWidget(parent = self.selectpanel)


        selectpanel_layout = QtGui.QVBoxLayout()
        selectpanel_layout.addWidget(self.mpw)
        selectpanel_layout.addWidget(self.foilnamelabel)
        selectpanel_layout.addWidget(self.openbutton)

        self.selectpanel.setLayout(selectpanel_layout)
        self.selectpanel.setFixedSize(600,200)

        self.selectpanel.connect(self.openbutton.openbutton,QtCore.SIGNAL('clicked()'),self.mpw.mpl.update_figure)
        self.selectpanel.connect(self.openbutton.openbutton,QtCore.SIGNAL('clicked()'),self.changelabel)

    def changelabel(self):
        self.foilnamelabel.setText(os.path.basename(self.mpw.mpl.filename))

class BaseFoilWidget(QtGui.QWidget):
    def __init__(self,parent = None):
        QtGui.QWidget.__init__(self, parent = parent)

        self.basepanel = QtGui.QWidget()

        self.no1 = FoilSelectWidget(parent = self.basepanel)
        self.no2 = FoilSelectWidget(parent = self.basepanel)
        self.no3 = FoilSelectWidget(parent = self.basepanel)
        self.no4 = FoilSelectWidget(parent = self.basepanel)

        basepanel_layout = QtGui.QVBoxLayout()
        basepanel_layout.addWidget(self.no1.selectpanel)
        basepanel_layout.addWidget(self.no2.selectpanel)
        basepanel_layout.addWidget(self.no3.selectpanel)
        basepanel_layout.addWidget(self.no4.selectpanel)

        self.basepanel.setLayout(basepanel_layout)

class GeneteticAlgolithm():
    def __init__(self):
        print("a")

    def getFoilChord(self,other):
        self.no1x = other.no1.mpw.mpl.Fx
        self.no1y = other.no1.mpw.mpl.Fy
        self.no2x = other.no2.mpw.mpl.Fx
        self.no2y = other.no2.mpw.mpl.Fy
        self.no3x = other.no3.mpw.mpl.Fx
        self.no3y = other.no3.mpw.mpl.Fy
        self.no4x = other.no4.mpw.mpl.Fx
        self.no4y = other.no4.mpw.mpl.Fy


    def defineFoil(self):
        self.x = numpy()
        print(self.x)
        for i in numpy.arange(1,100):
            self.x.append(numpy.power(i/100,2))
        print(self.x)


def main():
    qApp = QtGui.QApplication(sys.argv)
    main_window=QtGui.QMainWindow()

    basefoilpanel = BaseFoilWidget()
    main_window.setCentralWidget(basefoilpanel.basepanel)
    main_window.show()


    def exeGA():
        test = GeneteticAlgolithm()
        test.getFoilChord(basefoilpanel)
        test.defineFoil()

    basefoilpanel.no1.selectpanel.connect(basefoilpanel.no1.openbutton.openbutton,QtCore.SIGNAL('clicked()'),exeGA)
    sys.exit(qApp.exec_())

if __name__ == '__main__':
    main()

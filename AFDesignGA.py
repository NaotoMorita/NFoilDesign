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
        #self.selectpanel.setFixedSize(600,200)

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
        self.no = numpy.arange(0,101)
        self.x = self.no * self.no / 10000

        #-----finding foil Leading Edge テスト
        i = int(0)

        while self.no1x[i] > numpy.amin(self.no1x):
            i += 1
        self.no1LE = i + 1

        no1size = numpy.shape(self.no1x)[0]+1
        buttomy = numpy.flipud(numpy.interp(self.x[:],numpy.flipud(self.no1x[0:self.no1LE]),numpy.flipud(self.no1y[0:self.no1LE])))
        uppery = numpy.interp(self.x[:],self.no1x[self.no1LE-1:no1size],self.no1y[self.no1LE-1:no1size])
        #self.x = numpy.append(numpy.flipud(self.x),numpy.delete(self.x,0))
        self.y = numpy.append(buttomy,numpy.delete(uppery,0))

        #-----finding foil Leading Edge
        i = int(0)

        while self.no2x[i] > numpy.amin(self.no2x):
            i += 1
        self.no2LE = i + 1

        no2size = numpy.shape(self.no2x)[0]+1
        buttomy = numpy.flipud(numpy.interp(self.x[:],numpy.flipud(self.no2x[0:self.no2LE]),numpy.flipud(self.no2y[0:self.no2LE])))
        uppery = numpy.interp(self.x[:],self.no2x[self.no2LE-1:no2size],self.no2y[self.no2LE-1:no2size])
        #self.x = numpy.append(numpy.flipud(self.x),numpy.delete(self.x,0))
        self.y = numpy.vstack((self.y,numpy.append(buttomy,numpy.delete(uppery,0))))

        #-----finding foil Leading Edge
        i = int(0)

        while self.no3x[i] > numpy.amin(self.no3x):
            i += 1
        self.no3LE = i + 1

        no3size = numpy.shape(self.no3x)[0]+1
        buttomy = numpy.flipud(numpy.interp(self.x[:],numpy.flipud(self.no3x[0:self.no3LE]),numpy.flipud(self.no3y[0:self.no3LE])))
        uppery = numpy.interp(self.x[:],self.no3x[self.no3LE-1:no3size],self.no3y[self.no3LE-1:no3size])
        #self.x = numpy.append(numpy.flipud(self.x),numpy.delete(self.x,0))
        self.y = numpy.vstack((self.y,numpy.append(buttomy,numpy.delete(uppery,0))))

        #-----finding foil Leading Edge
        i = int(0)

        while self.no4x[i] > numpy.amin(self.no4x):
            i += 1
        self.no4LE = i + 1

        no4size = numpy.shape(self.no4x)[0]+1
        buttomy = numpy.flipud(numpy.interp(self.x[:],numpy.flipud(self.no4x[0:self.no4LE]),numpy.flipud(self.no4y[0:self.no4LE])))
        uppery = numpy.interp(self.x[:],self.no4x[self.no4LE-1:no4size],self.no4y[self.no4LE-1:no4size])
        self.x = numpy.append(numpy.flipud(self.x),numpy.delete(self.x,0))
        self.y = numpy.vstack((self.y,numpy.append(buttomy,numpy.delete(uppery,0))))


    def default_gene(self):

        self.parameter10 = [0]*n_sample
        self.gene2 = [0]*n_sample

        for n in range(n_sample):
            self.parameter10[n] = [random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095)]
            self.gene2[n] = [0,0,0,0,0,0,0,0]
            for i in range(8):
                self.gene2[n][i] = str(bin(self.parameter10[n][i]))[2:].zfill(12)

    def gene2coeficient(self):
        self.coeficient_ratio = [0]*n_sample
        self.coeficient = [0]*n_sample
        for n in range(n_sample):
            self.coeficient_ratio[n] = [0,0,0,0,0,0,0,0]
            self.coeficient[n] = [0,0,0,0,0,0,0,0]
            for i in range(8):
                self.coeficient_ratio[n][i] = int(self.gene2[n][i],2) / 4095

            self.coeficient[n][0] = 2*self.coeficient_ratio[n][0]-1
            self.coeficient[n][1] = 2*self.coeficient_ratio[n][1]-1
            self.coeficient[n][2] = 2*self.coeficient_ratio[n][2]-1
            self.coeficient[n][3] = 2*self.coeficient_ratio[n][3]-1
            self.coeficient[n][4] = 0.04*self.coeficient_ratio[n][4]-0.02  #zc
            self.coeficient[n][5] = 0.25*self.coeficient_ratio[n][5]+0.25  #xc
            self.coeficient[n][6] = 6*self.coeficient_ratio[n][6]-3        #alphaTE
            self.coeficient[n][7] = 1.4*self.coeficient_ratio[n][7]+0.6    #Amplifying coeficient



    def coeficient2foil(self):
        #-----make add-camberline
        for n in range(n_sample):
            xc = self.coeficient[n][5]
            zc = self.coeficient[n][4]
            alphaTE = self.coeficient[n][6]

            c_mat = numpy.arange(0, 4 * 4).reshape(4, 4) + numpy.identity(4)
            cu_vector = numpy.array([[zc],[0.0],[0.0],[scipy.tan(alphaTE * scipy.pi/180)]])
            for m in range(4):
                c_mat[0,m] = xc**(m+1)
                c_mat[1,m] = xc**(m) * (m+1)
                c_mat[2,m] = 1.0
                c_mat[3,m] = m+1.0
            camber_coeficient =numpy.linalg.solve(c_mat,cu_vector)
            addcamber = camber_coeficient[0] * self.x + camber_coeficient[1] * self.x**2 + camber_coeficient[2] * self.x**3 + camber_coeficient[3] * self.x ** 4


            if n == 0:
                self.y_GA =( self.y[0,:] * self.coeficient[n][0] + self.y[1,:] * self.coeficient[n][1] + self.y[2,:] * self.coeficient[n][2] + self.y[3,:] * self.coeficient[n][3] + addcamber) * self.coeficient[n][7]
            else:
                buff =( self.y[0,:] * self.coeficient[n][0] + self.y[1,:] * self.coeficient[n][1] + self.y[2,:] * self.coeficient[n][2] + self.y[3,:] * self.coeficient[n][3] + addcamber) * self.coeficient[n][7]
                self.y_GA = numpy.vstack((self.y_GA,buff))















def main():
    qApp = QtGui.QApplication(sys.argv)
    main_window=QtGui.QMainWindow()

    basefoilpanel = BaseFoilWidget()
    main_window.setCentralWidget(basefoilpanel.basepanel)
    main_window.show()

    global n_sample
    n_sample = 100
    def exeGA():
        test = GeneteticAlgolithm()
        test.getFoilChord(basefoilpanel)
        test.defineFoil()
        test.default_gene()
        test.gene2coeficient()
        test.coeficient2foil()


    basefoilpanel.no4.selectpanel.connect(basefoilpanel.no4.openbutton.openbutton,QtCore.SIGNAL('clicked()'),exeGA)
    sys.exit(qApp.exec_())

if __name__ == '__main__':
    main()

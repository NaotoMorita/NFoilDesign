﻿#-------------------------------------------------------------------------------
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
import scipy, numpy, math


import sys, os, random, copy
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

#import to exe XFoil
import subprocess
import shutil

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

class Matplot(matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=3, dpi=50, Fx = numpy.array([[0],[0]]), Fy = numpy.array([[0],[0]])):
        self.Fx = numpy.array(Fx)
        self.Fy = numpy.array(Fy)
        self.datax = 0.0
        self.datay = 0.0

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
        self.filename = "dae31.dat"
        foil = numpy.loadtxt(self.filename,skiprows=1)
        self.Fx = foil[:,0]
        self.Fy = foil[:,1]
        self.axes.plot(self.Fx, self.Fy)

    def update_figure(self):
        self.load()
        self.axes.plot(self.Fx, self.Fy)
        self.draw()

    def update_figure2(self):
        self.axes.plot(self.Fx, self.Fy)
        self.draw()

    def load(self):
        self.filename = QtGui.QFileDialog.getOpenFileName()
        foil = numpy.loadtxt(self.filename,skiprows=1)
        self.Fx = foil[:,0]
        self.Fy = foil[:,1]

class DataPlot(Matplot):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        Matplot.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.axes.set_aspect("auto")


    def update_figure(self,xlim = None, ylim = None, xlabel = "xlabel", ylabel = "ylabel"):
        self.axes.plot(self.datax, self.datay,marker='o',linewidth=0)
        self.axes.set_aspect("auto")
        if xlim != None:
            self.axes.set_xlim(xlim)
        if ylim != None:
            self.axes.set_ylim(ylim)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)


        self.draw()

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
        self.selectpanel.setFixedSize(500,200)

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


class CalclatedFoilWidget(QtGui.QWidget):
    def __init__(self,ga,foilno = 0,parent = None):
        QtGui.QWidget.__init__(self, parent = parent)

        self.itgcfw = QtGui.QWidget(parent = self)
        self.itgcfw.setFixedSize(800,300)


        self.cfw = FoilPlot(parent = self.itgcfw)
        self.cfw.Fx = ga.x
        self.cfw.Fy = ga.y_GA[foilno,:]
        self.cfw.compute_initial_figure()

        self.datapanel = QtGui.QWidget(parent = self.itgcfw)
        self.CLlabel = QtGui.QLabel()
        self.CLlabel.setText("CL : {CL}    Cd(count) : {Cd}    CL/Cd : {CLCd}    Thickness : {thn:4}".format(CL = round(ga.CL, 4), Cd = "NaN", CLCd = "NaN", thn = "NaN"))

        self.outputbutton = QtGui.QPushButton("EXPORT FOIL",parent = self.datapanel)

        datapanel_layout = QtGui.QHBoxLayout()
        datapanel_layout.addWidget(self.CLlabel)
        datapanel_layout.addWidget(self.outputbutton)
        self.datapanel.setLayout(datapanel_layout)

        itgcfw_layout = QtGui.QVBoxLayout()
        itgcfw_layout.addWidget(self.cfw)
        itgcfw_layout.addWidget(self.datapanel)
        self.itgcfw.setLayout(itgcfw_layout)



    def replot(self,ga,foilno = 0):
        self.cfw.Fx = ga.x
        self.cfw.Fy = ga.y_GA[foilno]
        self.cfw.update_figure2()
        self.CLlabel.setText("CL : {CL:5}    Cd(count) : {Cd:4}    CL/Cd : {CLCd:4}    Thickness : {thn:4}".format(CL = round(ga.CL, 4), Cd = round(ga.Cd * 10000,1), CLCd = round(ga.CL/ga.Cd,1), thn = round(ga.thn * 100,4)))

class InputWidget(QtGui.QWidget):
    def __init__(self,parent = None,):
        QtGui.QWidget.__init__(self, parent = parent)
        self.inputalpha = QtGui.QLineEdit(parent = self)
        self.inputalpha.setText('4')
        self.inputalpha.setFixedWidth(35)
        self.inputalpha.Normal = 4
        self.label_alpha = QtGui.QLabel(parent = self)
        self.label_alpha.setText("Alpha (deg):")


        self.inputRe = QtGui.QLineEdit(parent = self)
        self.inputRe.setText('500000')
        self.inputRe.setFixedWidth(50)
        self.label_Re = QtGui.QLabel(parent = self)
        self.label_Re.setText("  Reynolds No.:")


        self.inputCL = QtGui.QLineEdit(parent = self)
        self.inputCL.setText('1.1')
        self.inputCL.selectAll()
        self.inputCL.setFixedWidth(30)
        self.label_CL = QtGui.QLabel(parent = self)
        self.label_CL.setText("  CL :")

        self.inputthn = QtGui.QLineEdit(parent = self)
        self.inputthn.setText('11')
        self.inputthn.setFixedWidth(30)
        self.label_thn = QtGui.QLabel(parent = self)
        self.label_thn.setText("  Thickness (%):")

        self.inputthnpos = QtGui.QLineEdit(parent = self)
        self.inputthnpos.setText('36')
        self.inputthnpos.setFixedWidth(30)
        self.label_thnpos = QtGui.QLabel(parent = self)
        self.label_thnpos.setText("  Spar Position (%):")

        self.execute_button = QtGui.QPushButton("EXECUTION",parent=self)
        self.stop_button = QtGui.QPushButton("STOP",parent=self)
        self.default_button = QtGui.QPushButton("Default",parent=self)


        layout_inputwidget = QtGui.QHBoxLayout()
        layout_inputwidget.addWidget(self.label_alpha)
        layout_inputwidget.addWidget(self.inputalpha)
        layout_inputwidget.addWidget(self.label_Re)
        layout_inputwidget.addWidget(self.inputRe)
        layout_inputwidget.addWidget(self.label_CL)
        layout_inputwidget.addWidget(self.inputCL)
        layout_inputwidget.addWidget(self.label_thn)
        layout_inputwidget.addWidget(self.inputthn)
        layout_inputwidget.addWidget(self.label_thnpos)
        layout_inputwidget.addWidget(self.inputthnpos)
        layout_inputwidget.addWidget(self.default_button)
        layout_inputwidget.addWidget(self.execute_button)
        layout_inputwidget.addWidget(self.stop_button)


        self.setLayout(layout_inputwidget)

    def outputparameter(self):
        global alpha
        alpha = float(self.inputalpha.text())
        global Re
        Re = float(self.inputRe.text())
        global CL
        CL = float(self.inputCL.text())
        global thn
        thn = float(self.inputthn.text())/100
        global thnpos
        thnpos = float(self.inputthnpos.text())/100


class DataPlotWidget(QtGui.QWidget):
    def __init__(self,parent = None):
        QtGui.QWidget.__init__(self, parent = parent)

        self.main_widget = QtGui.QWidget(parent = self)
        evo_widget = QtGui.QWidget(parent = self.main_widget)

        self.Fconplot = DataPlot(parent = self.main_widget)
        self.Fconplot.compute_initial_figure()
        self.evo_CLCDplot = DataPlot(parent = evo_widget)
        self.evo_CLCDplot.compute_initial_figure()
        self.evo_thnplot = DataPlot(parent = evo_widget)
        self.evo_thnplot.compute_initial_figure()




        evo_widget_layout = QtGui.QVBoxLayout()
        evo_widget_layout.addWidget(self.evo_CLCDplot)
        evo_widget_layout.addWidget(self.evo_thnplot)
        evo_widget.setLayout(evo_widget_layout)

        main_widget_layout = QtGui.QHBoxLayout()
        main_widget_layout.addWidget(self.Fconplot)
        main_widget_layout.addWidget(evo_widget)
        self.main_widget.setLayout(main_widget_layout)

    def updata_dataplot(self,ga):
        self.Fconplot.datax = range(n_sample,0,-1)
        self.Fconplot.datay = ga.sortedlist[:,0]
        self.Fconplot.update_figure()
        self.evo_CLCDplot.datax = range(n_sample,0,-1)
        self.evo_CLCDplot.datay = ga.sortedlist[:,1]
        self.evo_CLCDplot.update_figure()
        self.evo_thnplot.datax = range(n_sample,0,-1)
        self.evo_thnplot.datay = ga.sortedlist[:,2]
        self.evo_thnplot.update_figure(ylim = [0,0.25])





class GeneteticAlgolithm():
    def __init__(self):
        if "self.x" in locals():
            pass
        else:
            self.x = 0
            self.y_GA = numpy.array([[0],[0]])
            self.CL = 0
            self.Cd = 100
            self.Cm = 0
            self.thn = 0

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

        for i in range(4):
            if max(self.y[i,0:99])>=max(self.y[i,101:198]):
                self.y[i,:] = numpy.flipud(self.y[i,:])

    def default_gene(self):

        self.parameter10 = [0]*n_sample
        self.gene2 = [0] * n_sample
        self.hash_GA = [0] * n_sample
        for n in range(n_sample):
            self.parameter10[n] = [random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095)]
            self.gene2[n] = [0,0,0,0,0,0,0,0]
            for i in range(8):
                self.gene2[n][i] = str(bin(self.parameter10[n][i]))[2:].zfill(12)
            self.hash_GA[n] = str(hash(str(self.gene2[n])))

        print

        self.save_topValue = 0

    def gene2coeficient(self):
        self.coeficient_ratio = [0]*n_sample
        self.coeficient = [0]*n_sample
        for n in range(n_sample):
            self.coeficient_ratio[n] = [0,0,0,0,0,0,0,0]
            self.coeficient[n] = [0,0,0,0,0,0,0,0]
            for i in range(8):
                self.coeficient_ratio[n][i] = float(int(self.gene2[n][i],2) / 4095)

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
                c_mat[3,m] = m + 1.0
            camber_coeficient =numpy.linalg.solve(c_mat,cu_vector)
            addcamber = camber_coeficient[0] * self.x + camber_coeficient[1] * self.x**2 + camber_coeficient[2] * self.x**3 + camber_coeficient[3] * self.x ** 4


            if n == 0:
                self.y_GA =( self.y[0,:] * self.coeficient[n][0] + self.y[1,:] * self.coeficient[n][1] + self.y[2,:] * self.coeficient[n][2] + self.y[3,:] * self.coeficient[n][3] + addcamber) * self.coeficient[n][7]
            else:
                buff =( self.y[0,:] * self.coeficient[n][0] + self.y[1,:] * self.coeficient[n][1] + self.y[2,:] * self.coeficient[n][2] + self.y[3,:] * self.coeficient[n][3] + addcamber) * self.coeficient[n][7]
                self.y_GA = numpy.vstack((self.y_GA,buff))

    def exeXFoil(self,qapp):




        self.CL_GA = [0.0]*n_sample
        self.Cd_GA = [0.0]*n_sample
        self.Cm_GA = [0.0]*n_sample
        self.thn_GA = [0.0]*n_sample
        self.CLCd_GA = [0.0]*n_sample

        for n in range(n_sample):
            #-----重い処理なのでイベント処理を挟む
            qapp.processEvents()
            self.thn_GA[n] = numpy.interp(thnpos,self.x[101:198],self.y_GA[n,101:198])-numpy.interp(thnpos,numpy.flipud(self.x[0:99]),numpy.flipud(self.y_GA[n,0:99]))
            #------xfoil analyze if thn_GA in correct range
            if self.thn_GA[n]<=thn*1.3 and self.thn_GA[n]>=thn*0.7 and self.hash_GA[n] not in self.hash_GA[n+1:n_sample] :
                print(n)
                fid = open("xfoil.foil",'w')
                fid.write("xfoil\n")
                for i in range(numpy.shape(self.x)[0]):
                    fid.write(" {x_ele}  {y_ele} \n".format(x_ele = self.x[i], y_ele = self.y_GA[n,i]))
                fid.close()
                #----execute CFoil
                try:
                    fname = "a0_pwrt.dat"
                    foil = "xfoil.foil"
                    ps = subprocess.Popen(['xfoil.exe'],stdin=subprocess.PIPE,stdout=None,stderr=None)
                    pipe = bytes("plop\n g\n\n load {load} \n oper\n visc {Re} \n iter 500\n pacc\n {filename} \n \n alfa{alpha}\n \n quit\n".format(load=foil,Re=Re,filename=fname,alpha=alpha),"ascii")
                    res = ps.communicate(pipe)


                    #----read XFoil Poler
                    anlydata = numpy.loadtxt(fname,skiprows=12)
                    if len(anlydata.shape)==2:
                        anlydata = analydata[-1,:]
                    os.remove(fname)

                    if math.isnan(float(sum(anlydata))):
                        raise

                    self.CL_GA[n] = anlydata[1]
                    self.Cd_GA[n] = anlydata[2]
                    self.Cm_GA[n] = anlydata[4]

                except:
                    self.CL_GA[n] = 0
                    self.Cd_GA[n] = 100
                    self.Cm_GA[n] = -100

            else:
                self.CL_GA[n] = 0
                self.Cd_GA[n] = 100
                self.Cm_GA[n] = -100

    def evaluete_cross(self):
        self.pfCd = 1
        self.pfCm = 0
        self.pfthn =10
        self.pfCL =5

        self.Fcon = [0]*n_sample
        for n in range(n_sample):
            if self.thn_GA[n] >= thn:
                self.Fcon[n] =(self.pfCd * 1 / self.Cd_GA[n] - self.pfCm * 1 / self.Cm_GA[n]) * numpy.exp(-self.pfthn * abs(self.thn_GA[n] - thn) - self.pfCL * abs(self.CL_GA[n] - CL))
            else:
                self.Fcon[n] =(self.pfCd * 1 / self.Cd_GA[n] - self.pfCm * 1 / self.Cm_GA[n]) * numpy.exp(-self.pfthn * 1.2 * abs(self.thn_GA[n] - thn) - self.pfCL * abs(self.CL_GA[n] - CL))
        self.maxFconNo = self.Fcon.index(max(self.Fcon))
        self.CL = self.CL_GA[self.maxFconNo]
        self.Cd = self.Cd_GA[self.maxFconNo]
        self.Cm = self.Cm_GA[self.maxFconNo]
        self.thn = self.thn_GA[self.maxFconNo]

        #-----最大値の保存
        if numpy.max(self.Fcon) > self.save_topValue:
            self.save_topValue = copy.deepcopy(self.Fcon[self.maxFconNo])
            self.save_top = copy.deepcopy(self.gene2[self.maxFconNo])
            print("saved")
            print(self.save_topValue)

        for n in range(n_sample):
            self.CLCd_GA[n] = self.CL_GA[n] / self.Cd_GA[n]

        #-----ソート
        self.sortedlist = numpy.zeros((n_sample,3))
        ind = numpy.argsort(self.Fcon)

        for i in range(n_sample):
            self.sortedlist[i,0] = self.Fcon[ind[i]]
            self.sortedlist[i,1] = self.CLCd_GA[ind[i]]
            self.sortedlist[i,2] = self.thn_GA[ind[i]]
        #-----sampleの総和を求める
        sumFcon = float(0)
        for n in range(n_sample-1):
            if self.hash_GA[n] in self.hash_GA[n+1:n_sample]:
                pass
            else:
                sumFcon += self.Fcon[n]

        sumFcon += self.Fcon[n_sample-1]

        self.surviveP = [float(0)] * n_sample
        for n in range(n_sample - 1):
            if self.hash_GA[n] in self.hash_GA[n+1:n_sample]:
                pass
            else:
                self.surviveP[n] = self.Fcon[n] / sumFcon
        self.surviveP[n_sample-1] = self.Fcon[n_sample-1] / sumFcon

        couple_GA = [0] * int(n_sample/2)
        for couple in range(int(n_sample/2)):
            couple_GA[couple] = [0,0]
            fatum = random.random()
            for i in range(n_sample):
                if i != 0:
                    if fatum > sum(self.surviveP[0:i]) and fatum <= sum(self.surviveP[0:i+1]) :
                        couple_GA[couple][0] = i
                        break
                else:
                    if fatum < self.surviveP[0]:
                        couple_GA[couple][0] = i
                        break

            fatum = random.random()
            for i in range(n_sample):
                if i != 0:
                    if fatum > sum(self.surviveP[0:i]) and fatum <= sum(self.surviveP[0:i+1]) :
                        couple_GA[couple][1] = i
                        break
                elif i==n_sample-1:
                    couple_GA[couple][1] = n_sample-1
                    print('bug')
                else:
                    if fatum < self.surviveP[0]:
                        couple_GA[couple][1] = i
                        break

        #-----交配
        for n in range(int(n_sample/2)):
            for i in range(8):
                cross_point = random.randint(2,10)
                #print(cross_point)

                cross1a = self.gene2[couple_GA[n][0]][i][cross_point:12]
                cross1b = self.gene2[couple_GA[n][0]][i][0:cross_point]
                cross2a = self.gene2[couple_GA[n][1]][i][cross_point:12]
                cross2b = self.gene2[couple_GA[n][1]][i][0:cross_point]
                #print([cross1a,cross1b]
                self.gene2[2*n][i] = cross1b+cross2a
                self.gene2[2*n+1][i] = cross2b+cross1a
        print(self.save_top)
        self.hash_GA = [0] * n_sample
        for n in range(n_sample):
            self.hash_GA[n] = str(hash(str(self.gene2[n])))
        #print(self.hash_GA)
        #print(self.gene2)
        #print(self.coeficient_ratio)
        print(couple_GA)
        print(self.surviveP)
        #print(sumFcon)
        #print(numpy.max(self.Fcon))
        #print(sum(self.surviveP))
        #print(self.Fcon[self.maxFconNo])

        #-----突然変異操作
        for n in range(n_sample):
            mutation = random.random()
            if mutation <= 0.05:
                i = random.randint(0,7)
                print("mutation is happened")
                rand_i = random.randint(1,10)
                if self.gene2[n][i][rand_i] == "0":
                    temp = self.gene2[n][i][0:rand_i]
                    self.gene2[n][i] = temp + "1"*(11-i)
                else:
                    temp =self.gene2[n][i][0:rand_i]
                    self.gene2[n][i] = temp + "0"*(11-i)

        self.gene2[n_sample-1] = copy.deepcopy(self.save_top)
































def main():
    qApp = QtGui.QApplication(sys.argv)
    main_window=QtGui.QMainWindow()


    main_panel = QtGui.QWidget()

    basefoilpanel = BaseFoilWidget(parent = main_panel)

    input_data_panel = QtGui.QWidget()

    input_widget = InputWidget(parent = input_data_panel)
    test = GeneteticAlgolithm()
    cfoil_widget = CalclatedFoilWidget(test,0,parent = input_data_panel)
    dataplotwidget = DataPlotWidget(parent = input_data_panel)
    input_data_panel_layput = QtGui.QVBoxLayout()
    input_data_panel_layput.addWidget(input_widget)
    input_data_panel_layput.addWidget(cfoil_widget.itgcfw)
    input_data_panel_layput.addWidget(dataplotwidget.main_widget)
    input_data_panel.setLayout(input_data_panel_layput)

    main_panel_layout = QtGui.QHBoxLayout()
    main_panel_layout.addWidget(input_data_panel)
    main_panel_layout.addWidget(basefoilpanel.basepanel)
    main_panel.setLayout(main_panel_layout)

    main_window.setCentralWidget(main_panel)
    main_window.show()

    global n_sample
    n_sample = 250
    if "done_default" in locals():
        pass
    else:
        done_default = 0

    def be_default():
        input_widget.outputparameter()

        test.getFoilChord(basefoilpanel)
        test.defineFoil()
        test.default_gene()
        done_default = 1
        print(done_default)



    def exeGA():
        print(done_default)
        #if done_default == 1:
        print("doing")
        test.gene2coeficient()
        test.coeficient2foil()
        test.exeXFoil(qApp)
        test.evaluete_cross()
        cfoil_widget.replot(test,test.maxFconNo)
        print("done")
        print(test.sortedlist)
        dataplotwidget.updata_dataplot(test)

    input_widget.connect(input_widget.default_button,QtCore.SIGNAL('clicked()'),be_default)
    input_widget.connect(input_widget.execute_button,QtCore.SIGNAL('clicked()'),exeGA)


    sys.exit(qApp.exec_())

if __name__ == '__main__':
    main()

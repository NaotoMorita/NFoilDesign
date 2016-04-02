#-------------------------------------------------------------------------------
# Name:XGAG (XFOIL Genetic Algorithm Gui airfoil design tool)
# Purpose:AirFoil Design
#
# Author:      NaotoMORITA
#
# Created:     10/31/2013
# Copyright:   (c) NaotoMORITA 2013
# Licence:     GPL
#-------------------------------------------------------------------------------

#-*- coding: utf-8 -*-
import numpy, csv, binstr

import sys, os, random, copy
from PyQt4 import QtGui, QtCore

import matplotlib.backends.backend_qt4agg
import matplotlib.backends.backend_agg


#import to exe XFoil
import subprocess
import shutil

global coe_range, coe_start
#             No1   No2   No3   No4   zc     xc     alphaTe  thn   sharing
coe_range = [ 2.0,  2.0,  2.0,  2.0,  0.030, 0.40,  6.0,     1.4,   0.025]
coe_start = [-1.0, -1.0, -1.0, -1.0, -0.015, 0.20, -3.0,     0.6,   0.025]


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
    def __init__(self,default, *args, **kwargs):
        Matplot.__init__(self, *args, **kwargs)
        self.foildirectory = default.foildirectory
        self.axes.tick_params(axis='both', which='major', labelsize=0)

    def compute_initial_figure(self,default_foil):
        self.filename = default_foil
        if not self.filename or not os.path.exists(self.filename):
            foil = numpy.array([[0.0,0.0],[0.0,0.0]])
            if os.path.exists("default.ini") and self.filename:
                QtGui.QMessageBox.warning(None,"foil open error", u"既定翼型の読込に失敗しました。リンク先を確認して下さい",
                                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                os.remove("default.ini")
                self.filename = ""
                self.foildirectory =""
        else:
            foil = numpy.loadtxt(self.filename,skiprows=1)

        self.Fx = foil[:,0]
        self.Fy = foil[:,1]
        self.axes.plot(self.Fx, self.Fy)

    def compute_initial_figure2(self,default_foil):
        self.filename = default_foil
        if not self.filename or not os.path.exists(self.filename):
            foil = numpy.array([[0.0,0.0],[0.0,0.0]])
            if os.path.exists("default.ini") and self.filename:
                QtGui.QMessageBox.warning(None,"foil open error", u"既定翼型の読込に失敗しました。リンク先を確認して下さい",
                                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                os.remove("default.ini")
                self.filename = ""
                self.foildirectory =""
        else:
            foil = numpy.loadtxt(self.filename,skiprows=1)
        self.Fx = foil[:,0]
        self.Fy = foil[:,1]
        self.axes.plot(self.Fx, self.Fy)
        self.draw()

    def update_figure(self):
        self.load()
        self.axes.plot(self.Fx, self.Fy)
        self.draw()

    def update_figure2(self):
        if not self.filename:
            foil = numpy.array([[0.0,0.0],[0.0,0.0]])
        else:
            foil = numpy.loadtxt(self.filename,skiprows=1)
        self.Fx = foil[:,0]
        self.Fy = foil[:,1]
        self.axes.plot(self.Fx, self.Fy)
        self.draw()


    def update_figure3(self):
        self.axes.plot(self.Fx, self.Fy)
        self.draw()

    def update_figure_mult(self,x,y):
        self.axes.plot(x,y)
        self.axes.set_ylim([-0.1,0.1])
        self.draw()

    def load(self):
        fid = open("default.ini",'r')
        self.foildirectory = fid.readline()
        self.foildirectory = self.foildirectory.rstrip("\n")
        fid.close()
        temp = copy.deepcopy(self.filename)
        self.filename = QtGui.QFileDialog.getOpenFileName(parent = None,caption = u"翼型を開く" ,directory=self.foildirectory, filter="Foil Chord File(*.dat *.txt)")
        if self.filename:
                foil = numpy.loadtxt(self.filename,skiprows=1)
                self.Fx = foil[:,0]
                self.Fy = foil[:,1]
        else:
            self.filename = temp





class DataPlot(Matplot):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        Matplot.__init__(self, *args, **kwargs)
        self.axes.tick_params(axis='both', which='major', labelsize=20)


    def compute_initial_figure(self):
        self.axes.set_aspect("auto")


    def update_figure(self,xlim = None, ylim = None, xlabel = "xlabel", ylabel = "ylabel",line_width = 0):
        self.axes.plot(self.datax, self.datay,marker='o',linewidth=line_width)
        self.axes.set_aspect("auto")
        if xlim != None:
            self.axes.set_xlim(xlim)
        if ylim != None:
            self.axes.set_ylim(ylim)
        self.axes.set_xlabel(xlabel,fontsize = 20)
        self.axes.set_ylabel(ylabel,fontsize = 20)
        self.axes.tick_params(axis='both', labelsize=20)

        self.draw()

class BaseFoilWidget(QtGui.QWidget):
    def __init__(self,default,parent = None):
        QtGui.QWidget.__init__(self, parent = parent)

        font = QtGui.QFont()
        font.setPointSize(12)

        self.basepanel = QtGui.QGroupBox(u"基準翼型",parent = self)
        self.basepanel.setFont(font)
        self.basepanel.setMinimumSize(150,600)
        self.basepanel.setMaximumSize(400,2000)






#第1翼型
        self.no1 = QtGui.QGroupBox(u"第1翼型",parent = self.basepanel)
        self.no1.showfoil = FoilPlot(default,parent = self.no1)
        self.no1.showfoil.compute_initial_figure(default.default_no1)
        self.no1.setTitle(u"第1翼型 - {foilname}".format(foilname = os.path.basename(self.no1.showfoil.filename)))
        self.no1.setFont(font)
        self.no1.openbutton = QtGui.QPushButton(u"第1翼型を開く")
        self.no1.openbutton.setFont(font)
        self.no1.coe_label = QtGui.QLabel(u"混合係数 : {coe}".format(coe = "--"))
        self.no1.layout = QtGui.QVBoxLayout()
        self.no1.layout.addWidget(self.no1.coe_label)
        self.no1.layout.addWidget(self.no1.showfoil)
        self.no1.layout.addWidget(self.no1.openbutton)
        self.no1.setLayout(self.no1.layout)

#第2翼型
        self.no2 = QtGui.QGroupBox(u"第2翼型",parent = self.basepanel)
        self.no2.showfoil = FoilPlot(default, parent = self.no2)
        self.no2.showfoil.compute_initial_figure(default.default_no2)
        self.no2.setTitle(u"第2翼型 - {foilname}".format(foilname = os.path.basename(self.no2.showfoil.filename)))
        self.no2.openbutton = QtGui.QPushButton(u"第2翼型を開く")
        self.no2.coe_label = QtGui.QLabel(u"混合係数 : {coe}".format(coe = "--"))
        self.no2.layout = QtGui.QVBoxLayout()
        self.no2.layout.addWidget(self.no2.coe_label)
        self.no2.layout.addWidget(self.no2.showfoil)
        self.no2.layout.addWidget(self.no2.openbutton)
        self.no2.setLayout(self.no2.layout)

#第3翼型
        self.no3 = QtGui.QGroupBox(u"第3翼型",parent = self.basepanel)
        self.no3.showfoil = FoilPlot(default, parent = self.no3)
        self.no3.showfoil.compute_initial_figure(default.default_no3)
        self.no3.setTitle(u"第3翼型 - {foilname}".format(foilname = os.path.basename(self.no3.showfoil.filename)))
        self.no3.openbutton = QtGui.QPushButton(u"第3翼型を開く")
        self.no3.coe_label = QtGui.QLabel(u"混合係数 : {coe}".format(coe = "--"))
        self.no3.layout = QtGui.QVBoxLayout()
        self.no3.layout.addWidget(self.no3.coe_label)
        self.no3.layout.addWidget(self.no3.showfoil)
        self.no3.layout.addWidget(self.no3.openbutton)
        self.no3.setLayout(self.no3.layout)

#第4翼型
        self.no4 = QtGui.QGroupBox(u"第4翼型",parent = self.basepanel)
        self.no4.showfoil = FoilPlot(default, parent = self.no4)
        self.no4.showfoil.compute_initial_figure(default.default_no4)
        self.no4.setTitle(u"第4翼型 - {foilname}".format(foilname = os.path.basename(self.no4.showfoil.filename)))
        self.no4.openbutton = QtGui.QPushButton(u"第4翼型を開く")
        self.no4.coe_label = QtGui.QLabel(u"混合係数 : {coe}".format(coe = "--"))
        self.no4.layout = QtGui.QVBoxLayout()
        self.no4.layout.addWidget(self.no4.coe_label)
        self.no4.layout.addWidget(self.no4.showfoil)
        self.no4.layout.addWidget(self.no4.openbutton)
        self.no4.setLayout(self.no4.layout)

#追加キャンバー
        self.acamb = QtGui.QGroupBox(u"追加キャンバー&&翼厚係数",parent = self.basepanel)
        self.acamb.showfoil = FoilPlot(default, parent = self.acamb)
        self.acamb.thnlabel = QtGui.QLabel(u"翼厚係数 : {coe}".format(coe = "--"))
        self.acamb.layout = QtGui.QVBoxLayout()
        self.acamb.layout.addWidget(self.acamb.showfoil)
        self.acamb.layout.addWidget(self.acamb.thnlabel)
        self.acamb.setLayout(self.acamb.layout)

        basepanel_layout = QtGui.QVBoxLayout()
        basepanel_layout.addWidget(self.no1)
        basepanel_layout.addWidget(self.no2)
        basepanel_layout.addWidget(self.no3)
        basepanel_layout.addWidget(self.no4)
        basepanel_layout.addWidget(self.acamb)

        self.basepanel.setLayout(basepanel_layout)

        self.no1.connect(self.no1.openbutton,QtCore.SIGNAL('clicked()'),self.updatefigure_changelabel_no1)
        self.no2.connect(self.no2.openbutton,QtCore.SIGNAL('clicked()'),self.updatefigure_changelabel_no2)
        self.no3.connect(self.no3.openbutton,QtCore.SIGNAL('clicked()'),self.updatefigure_changelabel_no3)
        self.no4.connect(self.no4.openbutton,QtCore.SIGNAL('clicked()'),self.updatefigure_changelabel_no4)

    def updatefigure_changelabel_no1(self):
        self.no1.showfoil.update_figure()
        self.no1.setTitle(u"第1翼型 - {foilname}".format(foilname = os.path.basename(self.no1.showfoil.filename)))
        #self.no1.foilnamelabel.setText(os.path.basename(self.no1.showfoil.filename))

    def updatefigure_changelabel_no2(self):
        self.no2.showfoil.update_figure()
        self.no2.setTitle(u"第2翼型 - {foilname}".format(foilname = os.path.basename(self.no2.showfoil.filename)))
        #self.no2.foilnamelabel.setText(os.path.basename(self.no2.showfoil.filename))

    def updatefigure_changelabel_no3(self):
        self.no3.showfoil.update_figure()
        self.no3.setTitle(u"第3翼型 - {foilname}".format(foilname = os.path.basename(self.no3.showfoil.filename)))
        #self.no3.foilnamelabel.setText(os.path.basename(self.no3.showfoil.filename))

    def updatefigure_changelabel_no4(self):
        self.no4.showfoil.update_figure()
        self.no4.setTitle(u"第4翼型 - {foilname}".format(foilname = os.path.basename(self.no4.showfoil.filename)))

        #self.no4.foilnamelabel.setText(os.path.basename(self.no4.showfoil.filename))

class CalclatedFoilWidget(QtGui.QWidget):
    def __init__(self, default, ga, foilno = 0, parent = None):
        QtGui.QWidget.__init__(self, parent = parent)
        font = QtGui.QFont()
        font.setPointSize(12)


        self.itgcfw = QtGui.QWidget(parent = self)
        self.itgcfw.setMinimumSize(500,150)

        self.cfw = FoilPlot(default, parent = self.itgcfw)
        self.cfw.Fx = ga.x
        self.cfw.Fy = ga.y_GA[foilno,:]
        self.cfw.compute_initial_figure("")

        self.datapanel = QtGui.QWidget(parent = self.itgcfw)
        self.CLlabel = QtGui.QLabel()
        self.CLlabel.setText(u"揚力係数CL : {CL}    抗力係数Cd(*10000) : {Cd}    揚抗比CL/Cd : {CLCd}    モーメント係数Cm : {Cm}     翼厚 : {thn:4}".format(CL = "--", Cd = "--", CLCd = "--",Cm = "--", thn = "--"))
        self.CLlabel.setFont(font)
        self.outputbutton = QtGui.QPushButton(u"翼型出力",parent = self.datapanel)
        self.outputbutton.setFont(font)

        self.outputbutton.setFixedWidth(100)
        self.rollbackbutton = QtGui.QPushButton(u"巻き戻し",parent = self.datapanel)
        self.rollbackbutton.setFont(font)
        self.rollbackbutton.setFixedWidth(100)
        self.combobox = QtGui.QComboBox()
        self.combobox.setFixedWidth(60)

        datapanel_layout = QtGui.QHBoxLayout()
        datapanel_layout.addWidget(self.CLlabel)
        datapanel_layout.addWidget(self.combobox)
        datapanel_layout.addWidget(self.outputbutton)
        datapanel_layout.addWidget(self.rollbackbutton)
        self.datapanel.setLayout(datapanel_layout)



        itgcfw_layout = QtGui.QVBoxLayout()
        itgcfw_layout.addWidget(self.cfw)
        itgcfw_layout.addWidget(self.datapanel)
        self.itgcfw.setLayout(itgcfw_layout)

    def replot(self,ga,foilno = 0):
        self.cfw.Fx = ga.x
        self.cfw.Fy = ga.y_GA[foilno]
        self.cfw.update_figure3()
        self.CLlabel.setText(u"CL : {CL:5}    Cd(count) : {Cd:4}    CL/Cd : {CLCd:4}    Cm : {Cm}     翼厚 : {thn:4}".format(CL = round(ga.CL, 4), Cd = round(ga.Cd * 10000,1), CLCd = round(ga.CL/ga.Cd,1),Cm = round(ga.Cm,4), thn = round(ga.thn * 100,4)))

    def replot2(self,ga):
        self.cfw.update_figure3()
        shownom = numpy.shape(ga.history_CL)[0]-1
        self.CLlabel.setText(u"CL : {CL:5}    Cd(count) : {Cd:4}    CL/Cd : {CLCd:4}    Cm : {Cm}     翼厚 : {thn:4}".format(CL = round(ga.history_CL[shownom], 4), Cd = round(ga.history_Cd[shownom] * 10000,1), CLCd = round(ga.history_CL[shownom]/ga.history_Cd[shownom],1),Cm = round(ga.history_Cm[shownom],4), thn = round(ga.history_thn[shownom] * 100,4)))


class Inputtarget_Setbutton_Widget(QtGui.QWidget):
    def __init__(self,parent = None,):
        QtGui.QWidget.__init__(self, parent = parent)

        self.basecontener = QtGui.QFrame(parent = self)
        self.basecontener.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken);
        self.inputwidget = QtGui.QWidget(parent =self.basecontener)

        self.inputwidget.inputalpha = QtGui.QLineEdit(parent = self)
        self.inputwidget.inputalpha.setText('4')
        self.inputwidget.inputalpha.setFixedWidth(35)
        self.inputwidget.inputalpha.Normal = 4
        self.inputwidget.label_alpha = QtGui.QLabel(parent = self)
        self.inputwidget.label_alpha.setText(u"設計パラメータ  迎角 (deg) :")


        self.inputwidget.inputRe = QtGui.QLineEdit(parent = self)
        self.inputwidget.inputRe.setText('500000')
        self.inputwidget.inputRe.setFixedWidth(50)
        self.inputwidget.label_Re = QtGui.QLabel(parent = self)
        self.inputwidget.label_Re.setText(u"  Reynolds数 :")


        self.inputwidget.inputCL = QtGui.QLineEdit(parent = self)
        self.inputwidget.inputCL.setText('1.2')
        self.inputwidget.inputCL.selectAll()
        self.inputwidget.inputCL.setFixedWidth(30)
        self.inputwidget.label_CL = QtGui.QLabel(parent = self)
        self.inputwidget.label_CL.setText(u"  揚力係数 :")

        self.inputwidget.inputthn = QtGui.QLineEdit(parent = self)
        self.inputwidget.inputthn.setText('11')
        self.inputwidget.inputthn.setFixedWidth(30)
        self.inputwidget.label_thn = QtGui.QLabel(parent = self)
        self.inputwidget.label_thn.setText(u"  翼厚 (%) :")

        self.inputwidget.inputthnpos = QtGui.QLineEdit(parent = self)
        self.inputwidget.inputthnpos.setText('36')
        self.inputwidget.inputthnpos.setFixedWidth(30)
        self.inputwidget.label_thnpos = QtGui.QLabel(parent = self)
        self.inputwidget.label_thnpos.setText(u"  翼厚計算位置 (%) :")

        self.inputwidget.inputminCd = QtGui.QLineEdit(parent = self)
        self.inputwidget.inputminCd.setText('65')
        self.inputwidget.inputminCd.setFixedWidth(20)
        self.inputwidget.label_minCd = QtGui.QLabel(parent = self)
        self.inputwidget.label_minCd.setText(u"  抗力係数下限 (count) :")



        layout_inputwidget = QtGui.QHBoxLayout()
        layout_inputwidget.addStretch(1)
        layout_inputwidget.addWidget(self.inputwidget.label_alpha)
        layout_inputwidget.addWidget(self.inputwidget.inputalpha)
        layout_inputwidget.addWidget(self.inputwidget.label_Re)
        layout_inputwidget.addWidget(self.inputwidget.inputRe)
        layout_inputwidget.addWidget(self.inputwidget.label_CL)
        layout_inputwidget.addWidget(self.inputwidget.inputCL)
        layout_inputwidget.addWidget(self.inputwidget.label_thn)
        layout_inputwidget.addWidget(self.inputwidget.inputthn)
        layout_inputwidget.addWidget(self.inputwidget.label_thnpos)
        layout_inputwidget.addWidget(self.inputwidget.inputthnpos)
        layout_inputwidget.addWidget(self.inputwidget.label_minCd)
        layout_inputwidget.addWidget(self.inputwidget.inputminCd)



        self.inputwidget.setLayout(layout_inputwidget)

#-----2行目、評価関数のパラメータを入力
        self.inputevafunc = QtGui.QWidget(parent = self.basecontener)
        self.inputevafunc.text1 = QtGui.QLabel(parent = self.inputevafunc)
        self.inputevafunc.text1.setText(u"評価関数 : (")
        self.inputevafunc.P1 = QtGui.QLineEdit(parent = self.inputevafunc)
        self.inputevafunc.P1.setText("1")
        self.inputevafunc.P1.setFixedWidth(30)
        self.inputevafunc.text2 = QtGui.QLabel(parent = self.inputevafunc)
        self.inputevafunc.text2.setText("* 1/Cd  +")
        self.inputevafunc.P2 = QtGui.QLineEdit(parent = self.inputevafunc)
        self.inputevafunc.P2.setText("0")
        self.inputevafunc.P2.setFixedWidth(30)
        self.inputevafunc.text3 = QtGui.QLabel(parent = self.inputevafunc)
        self.inputevafunc.text3.setText("* Exp(Cm) ) * Exp{ -")
        self.inputevafunc.P3 = QtGui.QLineEdit(parent = self.inputevafunc)
        self.inputevafunc.P3.setText("5")
        self.inputevafunc.P3.setFixedWidth(30)
        self.inputevafunc.text4 = QtGui.QLabel(parent = self.inputevafunc)
        self.inputevafunc.text4.setText("* |CL - CL(target)|  -")
        self.inputevafunc.P4 = QtGui.QLineEdit(parent = self.inputevafunc)
        self.inputevafunc.P4.setText("10")
        self.inputevafunc.P4.setFixedWidth(30)
        self.inputevafunc.text5 = QtGui.QLabel(parent = self.inputevafunc)
        self.inputevafunc.text5.setText(" * |thickness - thickness(target)|}")

        self.inputevafunc.layout = QtGui.QHBoxLayout()
        self.inputevafunc.layout.addStretch(1)
        self.inputevafunc.layout.addWidget(self.inputevafunc.text1)
        self.inputevafunc.layout.addWidget(self.inputevafunc.P1)
        self.inputevafunc.layout.addWidget(self.inputevafunc.text2)
        self.inputevafunc.layout.addWidget(self.inputevafunc.P2)
        self.inputevafunc.layout.addWidget(self.inputevafunc.text3)
        self.inputevafunc.layout.addWidget(self.inputevafunc.P3)
        self.inputevafunc.layout.addWidget(self.inputevafunc.text4)
        self.inputevafunc.layout.addWidget(self.inputevafunc.P4)
        self.inputevafunc.layout.addWidget(self.inputevafunc.text5)
        self.inputevafunc.setLayout(self.inputevafunc.layout)

        self.basecontener.layout = QtGui.QVBoxLayout()
        self.basecontener.layout.addWidget(self.inputwidget)
        self.basecontener.layout.addWidget(self.inputevafunc)
        self.basecontener.setLayout(self.basecontener.layout)


        font = QtGui.QFont()
        font.setPointSize(12)
        self.inputwidget.label_alpha.setFont(font)
        self.inputwidget.label_CL.setFont(font)
        self.inputwidget.label_Re.setFont(font)
        self.inputwidget.label_thn.setFont(font)
        self.inputwidget.label_thnpos.setFont(font)
        self.inputwidget.label_minCd.setFont(font)
        self.inputevafunc.text1.setFont(font)
        self.inputevafunc.text2.setFont(font)
        self.inputevafunc.text3.setFont(font)
        self.inputevafunc.text4.setFont(font)
        self.inputevafunc.text5.setFont(font)



class DataPlotWidget(QtGui.QWidget):
    def __init__(self,parent = None):
        QtGui.QWidget.__init__(self, parent = parent)

        self.main_widget = QtGui.QWidget(parent = self)
        frame = QtGui.QGroupBox(u"各個体の評価関数の値",parent = self.main_widget)
        frame.setMinimumSize(200,200)

        self.Fconplot = DataPlot(parent = frame)
        self.convhistory = QtGui.QTabWidget(parent = self.main_widget)
        self.convhistory.setMinimumSize(200,200)
        conv_widget = QtGui.QWidget(parent = self.convhistory)
        evo_widget = QtGui.QWidget(parent = self.convhistory)

        self.Fconplot.compute_initial_figure()
        frame_layout = QtGui.QHBoxLayout()
        frame_layout.addWidget(self.Fconplot)
        frame.setLayout(frame_layout)



        self.conv_CLplot = DataPlot(parent = conv_widget)
        self.conv_CLplot.compute_initial_figure()
        self.conv_CLCDplot = DataPlot(parent = conv_widget)
        self.conv_CLCDplot.compute_initial_figure()
        self.conv_thnplot = DataPlot(parent = conv_widget)
        self.conv_thnplot.compute_initial_figure()
        conv_widget_layout = QtGui.QVBoxLayout()
        conv_widget_layout.addWidget(self.conv_CLCDplot)
        conv_widget_layout.addWidget(self.conv_CLplot)
        conv_widget_layout.addWidget(self.conv_thnplot)
        conv_widget.setLayout(conv_widget_layout)


        self.evo_Fconplot = DataPlot(parent = evo_widget)
        self.evo_Fconplot.compute_initial_figure()
        self.evo_CLplot = DataPlot(parent = evo_widget)
        self.evo_CLplot.compute_initial_figure()
        self.evo_thnplot = DataPlot(parent = evo_widget)
        self.evo_thnplot.compute_initial_figure()
        evo_widget_layout = QtGui.QVBoxLayout()
        evo_widget_layout.addWidget(self.evo_Fconplot)
        evo_widget_layout.addWidget(self.evo_CLplot)
        evo_widget_layout.addWidget(self.evo_thnplot)
        evo_widget.setLayout(evo_widget_layout)

        self.convhistory.addTab(conv_widget,u"現世代")
        self.convhistory.addTab(evo_widget,u"履歴")

        main_widget_layout = QtGui.QHBoxLayout()
        main_widget_layout.addWidget(frame)
        main_widget_layout.addWidget(self.convhistory)
        self.main_widget.setLayout(main_widget_layout)

    def update_dataplot(self,ga,generation):


        self.Fconplot.datax = range(n_sample,0,-1)
        self.Fconplot.datay = ga.sortedlist[:,0]
        self.Fconplot.update_figure(ylabel = "Value of Evaluating Function",xlabel = "Individual")
        self.conv_CLplot.datax = range(n_sample,0,-1)
        self.conv_CLplot.datay = ga.sortedlist[:,3]
        self.conv_CLplot.update_figure(ylabel = "CL",xlabel = "Individual",ylim = [ga.CL_forplot*0.7,ga.CL_forplot*1.3])
        self.conv_CLCDplot.datax = range(n_sample,0,-1)
        self.conv_CLCDplot.datay = ga.sortedlist[:,1]
        self.conv_CLCDplot.update_figure(ylabel = "CL/Cd",xlabel = "Individual")
        self.conv_thnplot.datax = range(n_sample,0,-1)
        self.conv_thnplot.datay = ga.sortedlist[:,2] * 100
        self.conv_thnplot.update_figure(ylim = [ga.thn_forplot*70,ga.thn_forplot*130] ,ylabel = "Thickness",xlabel = "Individual")

        self.evo_Fconplot.datax = ga.history_generation

        self.evo_Fconplot.datay = ga.history_Fcon
        self.evo_Fconplot.update_figure(ylabel = "Val of EF",xlabel = "Generation",line_width = 1)
        self.evo_CLplot.datax = ga.history_generation
        self.evo_CLplot.datay = ga.history_CL
        self.evo_CLplot.update_figure(ylabel = "CL",xlabel = "Generation",line_width = 1)
        self.evo_thnplot.datax = ga.history_generation
        self.evo_thnplot.datay = ga.history_thn * 100
        self.evo_thnplot.update_figure(ylabel = "thickness(%)",xlabel = "Generation",line_width = 1)



class TitleExeStopProgressWidget(QtGui.QWidget):
    def __init__(self,parent = None):
        QtGui.QWidget.__init__(self, parent = parent)
        self.second = QtGui.QWidget(parent = self)
        self.titleprogress = QtGui.QWidget(parent = self)

        #self.title = QtGui.QLabel(("<font size = 10> XGAG </font> <font size = 5> -Genetic Algorithm Gui airfoil design tool-  </font>"))
        self.progressbar = QtGui.QProgressBar(None)
        self.progressbar.setFixedSize(300,30)
        self.savedonelabel = QtGui.QLabel(None)
        self.savedonelabel.setText("")



        font = QtGui.QFont()
        font.setPointSize(12)

        DEFAULT_STYLE = """
        QProgressBar{
        border: 2px solid grey;
        border-radius: 5px;
        text-align: center
        }

        QProgressBar::chunk {
        background-color: lightblue;
        width: 10px;
        margin: 1px;
        }
        """
        self.progressbar.setStyleSheet(DEFAULT_STYLE)


        self.indno = QtGui.QLabel(parent = self.second)
        self.indno.setText(u"個体数 : ")
        self.indno.setFont(font)
        self.inputindno = QtGui.QLineEdit(parent = self.second)
        self.inputindno.setFixedWidth(30)
        self.inputindno.setText("200")

        self.generation = QtGui.QLabel(parent = self.second)
        self.generation.setText(u"  世代 : 0 / ")
        self.generation.setFont(font)
        self.inputgeneration = QtGui.QLineEdit(parent = self.second)
        self.inputgeneration.setFixedWidth(30)
        self.inputgeneration.setText("50")

        self.exebutton = QtGui.QPushButton(u"計算")
        self.exebutton.setFixedWidth(70)
        self.exebutton.setFont(font)
        self.stopbutton = QtGui.QPushButton(u"一時停止")
        self.stopbutton.setFixedWidth(70)
        self.stopbutton.setFont(font)

        self.second.layout = QtGui.QHBoxLayout()
        self.second.layout.addStretch(1)
        self.second.layout.addWidget(self.progressbar)
        self.second.layout.addWidget(self.indno)
        self.second.layout.addWidget(self.inputindno)
        self.second.layout.addWidget(self.generation)
        self.second.layout.addWidget(self.inputgeneration)
        self.second.layout.addWidget(self.exebutton)
        self.second.layout.addWidget(self.stopbutton)
        self.second.setLayout(self.second.layout)

        #self.titleprogress.layout = QtGui.QHBoxLayout()
        #self.titleprogress.layout.addWidget(self.title)
        #self.titleprogress.layout.addWidget(self.progressbar)
        #self.titleprogress.setLayout(self.titleprogress.layout)

        self.layout = QtGui.QVBoxLayout()
        #self.layout.addWidget(self.titleprogress)
        self.layout.addWidget(self.second)
        self.setLayout(self.layout)



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
            self.run = 0
            self.generation = 0
            self.history_topValue = [0]
            self.history_top = [0]
            self.save_topValue = 0
            self.save_top = [0]
            self.n = 0
            self.pfCd = 0.0
            self.pfCm = 0.0
            self.pfCL = 0.0
            self.pfthn =0.0
            self.sortedlist =[]
            self.CL_forplot = 0
            self.thn_forplot = 0
            self.generation = 0
            self.hash_GA = []


    def getFoilChord(self,other):
        def normalize_foil(x,y):
            fid2 = open("foil.foil",'w')
            fid2.write("foil\n")
            for i in range(numpy.shape(x)[0]):
                fid2.write(" {x_ele}  {y_ele} \n".format(x_ele = x[i], y_ele = y[i]))
            fid2.close()
            foil = "foil.foil"
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            ps = subprocess.Popen(['xfoil.exe'],stdin=subprocess.PIPE,stdout=None,stderr=None,startupinfo=startupinfo)
            pipe = bytes("\nplop\n g\n\n norm\n load {load} \n pane\n GDES\n DERO\n eXec\n \n ppar \n n 300 \n \n \n save foil.foil\n y \n \n quit \n" .format(load=foil),"ascii")
            res = ps.communicate(pipe)

            foil = numpy.loadtxt("foil.foil",skiprows=1)
            x_out = foil[:,0]
            y_out = foil[:,1]
            return [x_out,y_out]


        no1xy = normalize_foil(other.no1.showfoil.Fx,other.no1.showfoil.Fy)
        self.no1x = no1xy[0]
        self.no1y = no1xy[1]
        no2xy = normalize_foil(other.no2.showfoil.Fx,other.no2.showfoil.Fy)
        self.no2x = no2xy[0]
        self.no2y = no2xy[1]
        no3xy = normalize_foil(other.no3.showfoil.Fx,other.no3.showfoil.Fy)
        self.no3x = no3xy[0]
        self.no3y = no3xy[1]
        no4xy = normalize_foil(other.no4.showfoil.Fx,other.no4.showfoil.Fy)
        self.no4x = no4xy[0]
        self.no4y = no4xy[1]

    def defineFoil(self):
        self.no = numpy.arange(0,101)
        self.x = (self.no / 100) ** 1.75

        #補間の種類
        sp_kind = "linear"

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

        self.genegray = [0] * n_sample
        for n in range(n_sample):
            self.genegray[n] = [0,0,0,0,0,0,0,0]

    def default_gene(self):

        self.parameter10 = [0]*n_sample
        self.gene2 = [0] * n_sample
        self.genegray = [0] * n_sample
        self.hash_GA = [0] * n_sample
        for n in range(n_sample):
            self.parameter10[n] = [random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095),random.randint(0,4095)]
            self.gene2[n] = [0,0,0,0,0,0,0,0]
            self.genegray[n] = [0,0,0,0,0,0,0,0]
            for i in range(8):
                self.gene2[n][i] = str(bin(self.parameter10[n][i]))[2:].zfill(12)




    def gene2coeficient(self):
        self.coefficient_ratio = [0]*n_sample
        self.coefficient = [0]*n_sample
        self.hash_GA = [0]*n_sample
        for n in range(n_sample):
            self.hash_GA[n] = str(hash(str(self.gene2[n])))
            self.coefficient_ratio[n] = [0,0,0,0,0,0,0,0]
            self.top_coefficient_ratio = [0,0,0,0,0,0,0,0]
            self.coefficient[n] = [0,0,0,0,0,0,0,0]
            self.top_coefficient = [0,0,0,0,0,0,0,0]
            for i in range(8):
                self.coefficient_ratio[n][i] = float(int(self.gene2[n][i],2) / 4095)

            self.coefficient[n][0] = coe_range[0]*self.coefficient_ratio[n][0]+coe_start[0]
            self.coefficient[n][1] = coe_range[1]*self.coefficient_ratio[n][1]+coe_start[1]
            self.coefficient[n][2] = coe_range[2]*self.coefficient_ratio[n][2]+coe_start[2]
            self.coefficient[n][3] = coe_range[3]*self.coefficient_ratio[n][3]+coe_start[3]
            self.coefficient[n][4] = coe_range[4]*self.coefficient_ratio[n][4]+coe_start[4]  #zc
            self.coefficient[n][5] = coe_range[5]*self.coefficient_ratio[n][5]+coe_start[5]  #xc
            self.coefficient[n][6] = coe_range[6]*self.coefficient_ratio[n][6]+coe_start[6]        #alphaTE
            self.coefficient[n][7] = coe_range[7]*self.coefficient_ratio[n][7]+coe_start[7]    #Amplifying coefficient

    def coeficient2foil(self):
        #-----make add-camberline
        for n in range(n_sample):
            xc = self.coefficient[n][5]
            zc = self.coefficient[n][4]
            alphaTE = self.coefficient[n][6]

            c_mat = numpy.arange(0, 4 * 4).reshape(4, 4) + numpy.identity(4)
            cu_vector = numpy.array([[zc],[0.0],[0.0],[numpy.tan(alphaTE * numpy.pi/180)]])
            for m in range(4):
                c_mat[0,m] = xc**(m+1)
                c_mat[1,m] = xc**(m) * (m+1)
                c_mat[2,m] = 1.0
                c_mat[3,m] = m + 1.0
            camber_coeficient =numpy.linalg.solve(c_mat,cu_vector)
            addcamber = camber_coeficient[0] * self.x + camber_coeficient[1] * self.x**2 + camber_coeficient[2] * self.x**3 + camber_coeficient[3] * self.x ** 4


            if n == 0:
                self.y_GA =( self.y[0,:] * self.coefficient[n][0] + self.y[1,:] * self.coefficient[n][1] + self.y[2,:] * self.coefficient[n][2] + self.y[3,:] * self.coefficient[n][3] + addcamber) * self.coefficient[n][7]
            else:
                buff =( self.y[0,:] * self.coefficient[n][0] + self.y[1,:] * self.coefficient[n][1] + self.y[2,:] * self.coefficient[n][2] + self.y[3,:] * self.coefficient[n][3] + addcamber) * self.coefficient[n][7]
                self.y_GA = numpy.vstack((self.y_GA,buff))

    def exeXFoil(self,qapp,titleexeprogress,evafunc):

        self.CL_GA = [0.0]*n_sample
        self.Cd_GA = [0.0]*n_sample
        self.Cm_GA = [0.0]*n_sample
        self.thn_GA = [0.0]*n_sample
        self.CLCd_GA = [0.0]*n_sample
        alpha = float(evafunc.inputwidget.inputalpha.text())
        Re = float(evafunc.inputwidget.inputRe.text())
        thn = float(evafunc.inputwidget.inputthn.text())/100
        thnpos = float(evafunc.inputwidget.inputthnpos.text())/100
        CL = float(evafunc.inputwidget.inputCL.text())
        Cd_target = float(evafunc.inputwidget.inputminCd.text())/10000


        for n in range(n_sample):
            #-----重い処理なのでイベント処理を挟む
            titleexeprogress.progressbar.setValue(int(n/(n_sample-1)*100))
            qapp.processEvents()
            if self.run != 0 and self.run !=2 :
                break

            self.thn_GA[n] = numpy.interp(thnpos,self.x[101:198],self.y_GA[n,101:198])-numpy.interp(thnpos,numpy.flipud(self.x[0:99]),numpy.flipud(self.y_GA[n,0:99]))
            #------xfoil analyze if thn_GA in correct range
            if self.thn_GA[n] <= thn * 1.5 and self.thn_GA[n] >= thn*0.5 and self.hash_GA[n] not in self.hash_GA[n+1:n_sample] :
                fid = open("xfoil.foil",'w')
                fid.write("xfoil\n")
                for i in range(numpy.shape(self.x)[0]):
                    fid.write(" {x_ele}  {y_ele} \n".format(x_ele = round(self.x[i],6), y_ele = round(self.y_GA[n,i],6)))
                fid.close()
                #----execute CFoil
                try:
                    fname = "a0_pwrt.dat"
                    foil = "xfoil.foil"
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    ps = subprocess.Popen(['xfoil.exe'],stdin=subprocess.PIPE,stdout=None,stderr=None,startupinfo=startupinfo)
                    pipe = bytes("\nplop\n g\n\n load {load} \n oper\n visc {Re} \n iter 100\n pacc\n {filename} \n \n alfa{alpha}\n \n quit\n".format(load=foil,Re=Re,filename=fname,alpha=alpha),"ascii")
                    res = ps.communicate(pipe)


                    #----read XFoil Poler

                    anlydata = numpy.loadtxt(fname,skiprows=12)


                    if len(anlydata.shape)==2:
                        anlydata = analydata[-1,:]
                    os.remove(fname)

                    if numpy.isnan(float(sum(anlydata))):
                        raise

                    self.CL_GA[n] = anlydata[1]
                    self.Cd_GA[n] = anlydata[2]
                    self.Cm_GA[n] = anlydata[4]

                except:
                    self.CL_GA[n] = 0
                    self.Cd_GA[n] = 100
                    self.Cm_GA[n] = -100

                if self.Cd_GA[n] <= Cd_target:
                    self.CL_GA[n] = 0
                    self.Cd_GA[n] = 100
                    self.Cm_GA[n] = -100

            else:
                self.CL_GA[n] = 0
                self.Cd_GA[n] = 100
                self.Cm_GA[n] = -100


    def evaluete_cross(self,evafunc,generation,savedonelabel):
        self.pfCd = float(evafunc.inputevafunc.P1.text())
        self.pfCm = float(evafunc.inputevafunc.P2.text())
        self.pfCL =float(evafunc.inputevafunc.P3.text())
        self.pfthn =float(evafunc.inputevafunc.P4.text())
        alpha = float(evafunc.inputwidget.inputalpha.text())
        Re = float(evafunc.inputwidget.inputRe.text())
        thn = float(evafunc.inputwidget.inputthn.text())/100
        self.thn_forplot = thn
        thnpos = float(evafunc.inputwidget.inputthnpos.text())/100
        CL = float(evafunc.inputwidget.inputCL.text())
        self.CL_forplot = CL
        Cd_target = float(evafunc.inputwidget.inputminCd.text())/10000

        #評価
        self.Fcon = [0]*n_sample
        for n in range(n_sample):
            if self.thn_GA[n] >= thn:
                self.Fcon[n] =(self.pfCd * 1 / self.Cd_GA[n] + self.pfCm * numpy.exp(self.Cm_GA[n])) * numpy.exp(-self.pfthn * abs(self.thn_GA[n] - thn) - self.pfCL * abs(self.CL_GA[n] - CL))
            else:
                self.Fcon[n] =(self.pfCd * 1 / self.Cd_GA[n] + self.pfCm * numpy.exp(self.Cm_GA[n])) * numpy.exp(-self.pfthn * abs(self.thn_GA[n] - thn) - self.pfCL * abs(self.CL_GA[n] - CL))

        #シェアリング
        #シェアリング半径
        self.sigma_s = coe_range[8]
        sharing = [0.0]*n_sample
        if self.sigma_s != 0.0:
            sharing = [0.0]*n_sample
            for n in range(n_sample):
                for i in range(n_sample):
                    if n != i:
                        #表現空間シェアリング
                        d = 0.0
                        for j in range(8):
                            d += (self.coefficient_ratio[n][j]- self.coefficient_ratio[i][j]) ** 2
                        d = numpy.sqrt(d)
                        sharing[n] += max(0,1-d / self.sigma_s)

        self.Fcon[n] = self.Fcon[n] / (1 + sharing[n])

        self.maxFconNo = self.Fcon.index(max(self.Fcon))
        self.CL = self.CL_GA[self.maxFconNo]
        self.Cd = self.Cd_GA[self.maxFconNo]
        self.Cm = self.Cm_GA[self.maxFconNo]
        self.thn = self.thn_GA[self.maxFconNo]


        if generation == 1:
            self.history_Fcon = numpy.array([0.0],dtype = "f")
            self.history_CL = numpy.array([0.0],dtype = "f")
            self.history_Cd = numpy.array([0.0],dtype = "f")
            self.history_Cm = numpy.array([0.0],dtype = "f")
            self.history_thn = numpy.array([0.0],dtype = "f")
            self.history_CLCD = numpy.array([0.0],dtype = "f")
            self.history_generation = numpy.array([0])
        else:
            self.history_Fcon = numpy.append(self.history_Fcon,[0.0])
            self.history_CL = numpy.append(self.history_CL,[0.0])
            self.history_Cd = numpy.append(self.history_Cd,[0.0])
            self.history_Cm = numpy.append(self.history_Cm,[0.0])
            self.history_thn = numpy.append(self.history_thn,[0.0])
            self.history_CLCD = numpy.append(self.history_CLCD,[0.0])
            self.history_generation = numpy.append(self.history_generation,0)



        int(generation)
        self.history_Fcon[generation-1] = copy.deepcopy(self.Fcon[self.maxFconNo])
        self.history_CL[generation-1] = copy.deepcopy(self.CL_GA[self.maxFconNo])
        self.history_Cd[generation-1] = copy.deepcopy(self.Cd_GA[self.maxFconNo])
        self.history_Cm[generation-1] = copy.deepcopy(self.Cm_GA[self.maxFconNo])
        self.history_thn[generation-1] = copy.deepcopy(self.thn_GA[self.maxFconNo])
        self.history_CLCD[generation-1] = copy.deepcopy(self.CL_GA[self.maxFconNo]/self.Cd_GA[self.maxFconNo])
        self.history_generation[generation-1] = copy.deepcopy(generation)


        #-----最大値の保存
        #保存個体の再計算
        self.save_topValue = 0.0
        if generation != 1:
            for i in range(8):
                self.top_coefficient_ratio[i] = float(int(self.save_top[i],2) / 4095)

            #ここから　上のGenetic Algolithm内と必ず一致させること
            self.top_coefficient[0] = coe_range[0]*self.top_coefficient_ratio[0]+coe_start[0]
            self.top_coefficient[1] = coe_range[1]*self.top_coefficient_ratio[1]+coe_start[1]
            self.top_coefficient[2] = coe_range[2]*self.top_coefficient_ratio[2]+coe_start[2]
            self.top_coefficient[3] = coe_range[3]*self.top_coefficient_ratio[3]+coe_start[3]
            self.top_coefficient[4] = coe_range[4]*self.top_coefficient_ratio[4]+coe_start[4]  #zc
            self.top_coefficient[5] = coe_range[5]*self.top_coefficient_ratio[5]+coe_start[5]  #xc
            self.top_coefficient[6] = coe_range[6]*self.top_coefficient_ratio[6]+coe_start[6]  #alphaTE
            self.top_coefficient[7] = coe_range[7]*self.top_coefficient_ratio[7]+coe_start[7]  #Amplifying coefficient
            #ここまで

            xc = self.top_coefficient[5]
            zc = self.top_coefficient[4]
            alphaTE = self.top_coefficient[6]

            c_mat = numpy.arange(0, 4 * 4).reshape(4, 4) + numpy.identity(4)
            cu_vector = numpy.array([[zc],[0.0],[0.0],[numpy.tan(alphaTE * numpy.pi/180)]])
            for m in range(4):
                c_mat[0,m] = xc**(m+1)
                c_mat[1,m] = xc**(m) * (m+1)
                c_mat[2,m] = 1.0
                c_mat[3,m] = m + 1.0
            camber_coeficient =numpy.linalg.solve(c_mat,cu_vector)
            self.top_addcamber = camber_coeficient[0] * self.x + camber_coeficient[1] * self.x**2 + camber_coeficient[2] * self.x**3 + camber_coeficient[3] * self.x ** 4
            self.top_x = self.x
            self.top_y =(self.y[0,:] * self.top_coefficient[0] + self.y[1,:] * self.top_coefficient[1] + self.y[2,:] * self.top_coefficient[2] + self.y[3,:] * self.top_coefficient[3] + self.top_addcamber) * self.top_coefficient[7]

            fid = open("top_foil.foil",'w')
            fid.write("top_foil\n")
            for i in range(numpy.shape(self.top_x)[0]):
                fid.write(" {x_ele}  {y_ele} \n".format(x_ele = self.top_x[i], y_ele = self.top_y[i]))
            fid.close()

            try:
                fname = "a0_pwrt.dat"
                foil = "top_foil.foil"
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW



                ps = subprocess.Popen(['xfoil.exe'],stdin=subprocess.PIPE,stdout=None,stderr=None,startupinfo=startupinfo)
                pipe = bytes("\nplop\n g\n\n load {load} \n oper\n visc {Re} \n iter 100\n pacc\n {filename} \n \n alfa{alpha}\n \n quit\n".format(load=foil,Re=Re,filename=fname,alpha=alpha),"ascii")
                res = ps.communicate(pipe)


                #----read XFoil Poler
                anlydata = numpy.loadtxt(fname,skiprows=12)

                if len(anlydata.shape)==2:
                    anlydata = analydata[-1,:]
                os.remove(fname)

                if numpy.isnan(float(sum(anlydata))):
                    raise

                self.top_CL = anlydata[1]
                self.top_Cd = anlydata[2]
                self.top_Cm = anlydata[4]

            except:
                self.top_CL = 0
                self.top_Cd = 100
                self.top_Cm = -100

            if self.top_Cd <= Cd_target:
                self.top_CL = 0
                self.top_Cd = 100
                self.top_Cm = -100

            self.top_thn = numpy.interp(thnpos,self.top_x[101:198],self.top_y[101:198])-numpy.interp(thnpos,numpy.flipud(self.top_x[0:99]),numpy.flipud(self.top_y[0:99]))
            self.save_topValue = (self.pfCd * 1 / self.top_Cd + self.pfCm * numpy.exp(self.top_Cm)) * numpy.exp(-self.pfthn * abs(self.top_thn - thn) - self.pfCL * abs(self.top_CL - CL))

                    #シェアリング
            #シェアリング半径
            sharing_top = 0.0
            if self.sigma_s != 0.0:
                for i in range(n_sample):
                    #表現空間シェアリング
                    d = 0.0
                    for j in range(8):
                        d += (self.top_coefficient_ratio[j]- self.coefficient_ratio[i][j]) ** 2
                    d = numpy.sqrt(d)
                    sharing_top += max(0,1 - d / self.sigma_s)

            if sharing_top != 0:
                self.save_topValue = self.save_topValue / (sharing_top)
            else:
                self.save_topValue = self.save_topValue / (1 + sharing_top)


        savedonelabel.clear()
        savedonelabel.setText("")
        if numpy.max(self.Fcon) > self.save_topValue:
            savedonelabel.setText(u"進化！")
            self.save_top = copy.deepcopy(self.gene2[self.maxFconNo])

        for n in range(n_sample):
            self.CLCd_GA[n] = self.CL_GA[n] / self.Cd_GA[n]

        if generation != 1:
            self.history_topValue.append([0])
            self.history_top.append([0])
        #最大値の値の再計算(1回目）（これで計算中の設定値の変更が可能になる。
        #保存個体の再計算
        if generation == 1:
            for i in range(8):
                self.top_coefficient_ratio[i] = float(int(self.save_top[i],2) / 4095)

            #ここから　上のGenetic Algolithm内と必ず一致させること
            self.top_coefficient[0] = coe_range[0]*self.top_coefficient_ratio[0]+coe_start[0]
            self.top_coefficient[1] = coe_range[1]*self.top_coefficient_ratio[1]+coe_start[1]
            self.top_coefficient[2] = coe_range[2]*self.top_coefficient_ratio[2]+coe_start[2]
            self.top_coefficient[3] = coe_range[3]*self.top_coefficient_ratio[3]+coe_start[3]
            self.top_coefficient[4] = coe_range[4]*self.top_coefficient_ratio[4]+coe_start[4]  #zc
            self.top_coefficient[5] = coe_range[5]*self.top_coefficient_ratio[5]+coe_start[5]  #xc
            self.top_coefficient[6] = coe_range[6]*self.top_coefficient_ratio[6]+coe_start[6]  #alphaTE
            self.top_coefficient[7] = coe_range[7]*self.top_coefficient_ratio[7]+coe_start[7]  #Amplifying coefficient
            #ここまで

            xc = self.top_coefficient[5]
            zc = self.top_coefficient[4]
            alphaTE = self.top_coefficient[6]

            c_mat = numpy.arange(0, 4 * 4).reshape(4, 4) + numpy.identity(4)
            cu_vector = numpy.array([[zc],[0.0],[0.0],[numpy.tan(alphaTE * numpy.pi/180)]])
            for m in range(4):
                c_mat[0,m] = xc**(m+1)
                c_mat[1,m] = xc**(m) * (m+1)
                c_mat[2,m] = 1.0
                c_mat[3,m] = m + 1.0
            camber_coeficient =numpy.linalg.solve(c_mat,cu_vector)
            self.top_addcamber = camber_coeficient[0] * self.x + camber_coeficient[1] * self.x**2 + camber_coeficient[2] * self.x**3 + camber_coeficient[3] * self.x ** 4
            self.top_x = self.x
            self.top_y =(self.y[0,:] * self.top_coefficient[0] + self.y[1,:] * self.top_coefficient[1] + self.y[2,:] * self.top_coefficient[2] + self.y[3,:] * self.top_coefficient[3] + self.top_addcamber) * self.top_coefficient[7]

            fid = open("top_foil.foil",'w')
            fid.write("top_foil\n")
            for i in range(numpy.shape(self.top_x)[0]):
                fid.write(" {x_ele}  {y_ele} \n".format(x_ele = self.top_x[i], y_ele = self.top_y[i]))
            fid.close()

            try:
                fname = "a0_pwrt.dat"
                foil = "top_foil.foil"
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW



                ps = subprocess.Popen(['xfoil.exe'],stdin=subprocess.PIPE,stdout=None,stderr=None,startupinfo=startupinfo)
                pipe = bytes("\nplop\n g\n\n load {load} \n oper\n visc {Re} \n iter 100\n pacc\n {filename} \n \n alfa{alpha}\n \n quit\n".format(load=foil,Re=Re,filename=fname,alpha=alpha),"ascii")
                res = ps.communicate(pipe)


                #----read XFoil Poler
                anlydata = numpy.loadtxt(fname,skiprows=12)

                if len(anlydata.shape)==2:
                    anlydata = analydata[-1,:]
                os.remove(fname)

                if numpy.isnan(float(sum(anlydata))):
                    raise

                self.top_CL = anlydata[1]
                self.top_Cd = anlydata[2]
                self.top_Cm = anlydata[4]

            except:
                self.top_CL = 0
                self.top_Cd = 100
                self.top_Cm = -100

            if self.top_Cd <= Cd_target:
                self.top_CL = 0
                self.top_Cd = 100
                self.top_Cm = -100

            self.top_thn = numpy.interp(thnpos,self.top_x[101:198],self.top_y[101:198])-numpy.interp(thnpos,numpy.flipud(self.top_x[0:99]),numpy.flipud(self.top_y[0:99]))
            self.save_topValue = (self.pfCd * 1 / self.top_Cd + self.pfCm * numpy.exp(self.top_Cm)) * numpy.exp(-self.pfthn * abs(self.top_thn - thn) - self.pfCL * abs(self.top_CL - CL))

        self.history_topValue[generation-1] = copy.deepcopy(self.save_topValue)
        self.history_top[generation-1] = copy.deepcopy(self.save_top)





        #-----ソート
        self.sortedlist = numpy.zeros((n_sample,4))
        ind = numpy.argsort(self.Fcon)

        for i in range(n_sample):
            self.sortedlist[i,0] = self.Fcon[ind[i]]
            self.sortedlist[i,1] = self.CLCd_GA[ind[i]]
            self.sortedlist[i,2] = self.thn_GA[ind[i]]
            self.sortedlist[i,3] = self.CL_GA[ind[i]]
        #-----sampleの総和を求める
        sumFcon = float(0)
        for n in range(n_sample-1):
            if self.hash_GA[n] in self.hash_GA[n+1:n_sample]:
                pass
            else:
                sumFcon += self.Fcon[n]

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
                else:
                    if fatum < self.surviveP[0]:
                        couple_GA[couple][1] = i
                        break

        #-----交配
        #バイナリからグレイコードへの変換
        for n in range (n_sample):
            for i in range(8):
                self.genegray[n][i] = binstr.b_bin_to_gray(self.gene2[n][i])

        for n in range(int(n_sample/2)):
            for i in range(8):
                cross_point = random.randint(1,10)

                cross1a = self.genegray[couple_GA[n][0]][i][cross_point:12]
                cross1b = self.genegray[couple_GA[n][0]][i][0:cross_point]
                cross2a = self.genegray[couple_GA[n][1]][i][cross_point:12]
                cross2b = self.genegray[couple_GA[n][1]][i][0:cross_point]

                self.genegray[2*n][i] = str(cross1b+cross2a).zfill(12)

                self.genegray[2*n+1][i] = str(cross2b+cross1a).zfill(12)

        #-----突然変異操作
        for n in range(n_sample):
            mutation = random.random()
            if mutation <= 0.07:
                i = random.randint(0,7)

                rand_i = random.randint(0,10)
                temp = self.genegray[n][i][0:rand_i]
                while len(temp) < 12:
                    temp = temp + str(random.randint(0,1))

        #グレイコードからバイナリへの変換
        for n in range (n_sample):
            for i in range(8):
                self.gene2[n][i] = binstr.b_gray_to_bin(self.genegray[n][i])

        self.hash_GA = [0] * n_sample




        self.gene2[n_sample-1] = copy.deepcopy(self.save_top)

class Export_Filt_Foil():
    def __init__(self):
        self.export_gene = [0,0,0,0,0,0,0,0]
        self.exprt_coefficient_ratio = [0,0,0,0,0,0,0,0]
        self.exprt_coefficient = [0,0,0,0,0,0,0,0]
        self.exfail = 0

    def gene2foil(self,ga,generation):
        self.export_gene = ga.history_top[generation-1]

        for i in range(8):
            self.exprt_coefficient_ratio[i] = float(int(self.export_gene[i],2) / 4095)

        #ここから　上のGenetic Algolithm内と必ず一致させること
        self.exprt_coefficient[0] = coe_range[0]*self.exprt_coefficient_ratio[0]+coe_start[0]
        self.exprt_coefficient[1] = coe_range[1]*self.exprt_coefficient_ratio[1]+coe_start[1]
        self.exprt_coefficient[2] = coe_range[2]*self.exprt_coefficient_ratio[2]+coe_start[2]
        self.exprt_coefficient[3] = coe_range[3]*self.exprt_coefficient_ratio[3]+coe_start[3]
        self.exprt_coefficient[4] = coe_range[4]*self.exprt_coefficient_ratio[4]+coe_start[4]  #zc
        self.exprt_coefficient[5] = coe_range[5]*self.exprt_coefficient_ratio[5]+coe_start[5]  #xc
        self.exprt_coefficient[6] = coe_range[6]*self.exprt_coefficient_ratio[6]+coe_start[6]  #alphaTE
        self.exprt_coefficient[7] = coe_range[7]*self.exprt_coefficient_ratio[7]+coe_start[7]  #Amplifying coefficient
        #ここまで

        xc = self.exprt_coefficient[5]
        zc = self.exprt_coefficient[4]
        alphaTE = self.exprt_coefficient[6]

        c_mat = numpy.arange(0, 4 * 4).reshape(4, 4) + numpy.identity(4)
        cu_vector = numpy.array([[zc],[0.0],[0.0],[numpy.tan(alphaTE * numpy.pi/180)]])
        for m in range(4):
            c_mat[0,m] = xc**(m+1)
            c_mat[1,m] = xc**(m) * (m+1)
            c_mat[2,m] = 1.0
            c_mat[3,m] = m + 1.0
        camber_coeficient =numpy.linalg.solve(c_mat,cu_vector)
        addcamber = camber_coeficient[0] * ga.x + camber_coeficient[1] * ga.x**2 + camber_coeficient[2] * ga.x**3 + camber_coeficient[3] * ga.x ** 4
        self.export_x = ga.x
        self.export_y =(ga.y[0,:] * self.exprt_coefficient[0] + ga.y[1,:] * self.exprt_coefficient[1] + ga.y[2,:] * self.exprt_coefficient[2] + ga.y[3,:] * self.exprt_coefficient[3] + addcamber) * self.exprt_coefficient[7]

        fid = open("export.foil",'w')
        fid.write("export\n")
        for i in range(numpy.shape(self.export_x)[0]):
            fid.write(" {x_ele}  {y_ele} \n".format(x_ele = self.export_x[i], y_ele = self.export_y[i]))
        fid.close()

    def filt_foil(self,alpha):
        foil = "export.foil"
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        ps = subprocess.Popen(['xfoil.exe'],stdin=subprocess.PIPE,stdout=None,stderr=None,startupinfo=startupinfo)
        pipe = bytes("\nplop\n g\n\n load {load} \n oper\n alfa{alpha}\n \n mdes \n aq {alpha} \n filt \n exec\n\n pcop \n save export.foil \n Y \n quit\n".format(load=foil,alpha=alpha),"ascii")
        res = ps.communicate(pipe)

        foil = numpy.loadtxt("export.foil",skiprows=1)
        self.export_x = foil[:,0]
        self.export_y = foil[:,1]

    def do_export(self):
        try:
            fid = open(self.export_foilname,'w')
            fid.write("{foilname}\n".format(foilname = os.path.splitext(os.path.basename(self.export_foilname))[0]))
            for i in range(numpy.shape(self.export_x)[0]):
                fid.write(" {x_ele}  {y_ele} \n".format(x_ele = round(self.export_x[i],6), y_ele = round(self.export_y[i],6)))
            fid.close()
            os.remove("export.foil")
            self.exfail = 0
        except:
            self.exfail = 1


    def dialog(self,cfoil_widget,input_widget,default):
        ret = QtGui.QMessageBox.question(None,u"翼型出力",
                        u"世代:{generation}を出力します\n速度分布の平滑化行いますか？".format(generation = int(cfoil_widget.combobox.currentText())),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.export_foilname = QtGui.QFileDialog.getSaveFileName(None, caption = u"翼型出力(速度分布平滑化))",
                                    directory = os.path.join(default.foildirectory,"XGAGf{generation}".format(generation =
                                    int(cfoil_widget.combobox.currentText()))), filter = "Foil Chord File(*.dat)")
            alpha = float(input_widget.inputwidget.inputalpha.text())
            self.filt_foil(alpha)
            self.do_export()
        elif ret == QtGui.QMessageBox.No:
            self.export_foilname = QtGui.QFileDialog.getSaveFileName(None, caption = u"翼型出力(速度分布平滑化無し)",
                                    directory = os.path.join(default.foildirectory,"XGAGf{generation}".format(generation =
                                    int(cfoil_widget.combobox.currentText()))), filter = "Foil Chord File(*.dat)")
            self.do_export()






class Foils_Default_Change(QtGui.QWidget):
    def __init__(self,parent = None):
        QtGui.QWidget.__init__(self, parent = parent)
        self.read_init_file()

        self.foildirectory = ""
        self.default_no1 = ""
        self.default_no2 = ""
        self.default_no3 = ""
        self.default_no4 = ""

    def read_init_file(self):
        try:
            fidr = open("default.ini",'r')
            self.foildirectory = fidr.readline()
            self.foildirectory = self.foildirectory.rstrip("\n")
            self.default_no1 = fidr.readline()
            self.default_no1 = self.default_no1.rstrip("\n")
            self.default_no2 = fidr.readline()
            self.default_no2 = self.default_no2.rstrip("\n")
            self.default_no3 = fidr.readline()
            self.default_no3 = self.default_no3.rstrip("\n")
            self.default_no4 = fidr.readline()
            self.default_no4 = self.default_no4.rstrip("\n")
            fidr.close()
        except:
            self.foildirectory = "FOILS"
            self.default_no1 = ""
            self.default_no2 = ""
            self.default_no3 = ""
            self.default_no4 = ""
            self.wirte_init_file()
            if not os.path.exists("FOILS"):
                os.mkdir("FOILS")




    def wirte_init_file(self):
        fidw = open("default.ini",'w')
        fidw.write("{dir}\n{no1}\n{no2}\n{no3}\n{no4}\n".format(dir = self.foildirectory, no1 = self.default_no1, no2 = self.default_no2, no3 = self.default_no3, no4 = self.default_no4))
        fidw.close()


    def change_dialog(self):
        font = QtGui.QFont()
        font.setPointSize(12)
        def change_dir():
            self.foildirectory = QtGui.QFileDialog.getExistingDirectory(parent = None,caption = "FOIL Directory" ,directory=self.foildirectory)
            if not self.foildirectory:
                self.foildirectory = os.path.join(os.getcwd(),"FOILS")
            self.defaultdirectory.current_dir_show.setText(self.foildirectory)
            self.defaultdirectory.current_dir_show.setFont(font)

            self.wirte_init_file()

        def change_foil_no1():
            self.default_no1 = QtGui.QFileDialog.getOpenFileName(parent = None,caption = "OPEN FOIL" ,directory=self.foildirectory, filter="Foil Chord File(*.dat *.txt)")
            self.defaultfoil.no1.currentfoil.setText(self.default_no1)
            self.defaultfoil.no1.currentfoil.setFont(font)
            self.wirte_init_file()

        def change_foil_no2():
            self.default_no2 = QtGui.QFileDialog.getOpenFileName(parent = None,caption = "OPEN FOIL" ,directory=self.foildirectory, filter="Foil Chord File(*.dat *.txt)")
            self.defaultfoil.no2.currentfoil.setText(self.default_no2)
            self.defaultfoil.no2.currentfoil.setFont(font)
            self.wirte_init_file()

        def change_foil_no3():
            self.default_no3 = QtGui.QFileDialog.getOpenFileName(parent = None,caption = "OPEN FOIL" ,directory=self.foildirectory, filter="Foil Chord File(*.dat *.txt)")
            self.defaultfoil.no3.currentfoil.setText(self.default_no3)
            self.defaultfoil.no3.currentfoil.setFont(font)
            self.wirte_init_file()

        def change_foil_no4():
            self.default_no4 = QtGui.QFileDialog.getOpenFileName(parent = None,caption = "OPEN FOIL" ,directory=self.foildirectory, filter="Foil Chord File(*.dat *.txt)")
            self.defaultfoil.no4.currentfoil.setText(self.default_no4)
            self.wirte_init_file()


        self.dialog = QtGui.QDialog(parent = None)
        self.dialog.setWindowTitle(u"既定翼型設定")
        self.dialog.setModal(1)
        self.dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.dialog.setFixedSize(700,400)

        self.defaultdirectory = QtGui.QGroupBox(u"翼型保存フォルダ",parent = self.dialog)
        self.defaultdirectory.setFont(font)
        self.defaultdirectory.current_dir_show = QtGui.QLabel(parent = self.defaultdirectory)
        self.defaultdirectory.current_dir_show.setText(self.foildirectory)
        self.defaultdirectory.changebutton = QtGui.QPushButton(u"変更",parent = self.defaultdirectory)
        self.defaultdirectory.changebutton.setFixedWidth(50)
        self.defaultdirectory.layout = QtGui.QHBoxLayout()
        self.defaultdirectory.layout.addWidget(self.defaultdirectory.current_dir_show)
        self.defaultdirectory.layout.addWidget(self.defaultdirectory.changebutton)
        self.defaultdirectory.setLayout(self.defaultdirectory.layout)

        self.defaultfoil = QtGui.QGroupBox(u"デフォルト翼型")
        self.defaultfoil.setFont(font)


        self.defaultfoil.no1 =QtGui.QGroupBox("No.1")
        self.defaultfoil.no1.setFont(font)
        self.defaultfoil.no2 =QtGui.QGroupBox("No.2")
        self.defaultfoil.no2.setFont(font)
        self.defaultfoil.no3 =QtGui.QGroupBox("No.3")
        self.defaultfoil.no3.setFont(font)
        self.defaultfoil.no4 =QtGui.QGroupBox("No.4")
        self.defaultfoil.no4.setFont(font)

        self.defaultfoil.no1.currentfoil = QtGui.QLabel(parent = self.defaultfoil.no1)
        self.defaultfoil.no1.currentfoil.setText(self.default_no1)
        self.defaultfoil.no1.currentfoil.setFont(font)
        self.defaultfoil.no1.changebutton = QtGui.QPushButton(u"変更",parent = self.defaultfoil.no1)
        self.defaultfoil.no1.changebutton.setFixedWidth(50)

        self.defaultfoil.no2.currentfoil = QtGui.QLabel(parent = self.defaultfoil.no2)
        self.defaultfoil.no2.currentfoil.setText(self.default_no2)
        self.defaultfoil.no2.currentfoil.setFont(font)
        self.defaultfoil.no2.changebutton = QtGui.QPushButton(u"変更",parent = self.defaultfoil.no2)
        self.defaultfoil.no2.changebutton.setFixedWidth(50)

        self.defaultfoil.no3.currentfoil = QtGui.QLabel(parent = self.defaultfoil.no3)
        self.defaultfoil.no3.currentfoil.setText(self.default_no3)
        self.defaultfoil.no3.currentfoil.setFont(font)
        self.defaultfoil.no3.changebutton = QtGui.QPushButton(u"変更",parent = self.defaultfoil.no3)
        self.defaultfoil.no3.changebutton.setFixedWidth(50)

        self.defaultfoil.no4.currentfoil = QtGui.QLabel(parent = self.defaultfoil.no4)
        self.defaultfoil.no4.currentfoil.setText(self.default_no4)
        self.defaultfoil.no4.currentfoil.setFont(font)
        self.defaultfoil.no4.changebutton = QtGui.QPushButton(u"変更",parent = self.defaultfoil.no4)
        self.defaultfoil.no4.changebutton.setFixedWidth(50)

        self.defaultfoil.no1.layout = QtGui.QHBoxLayout()
        self.defaultfoil.no1.layout.addWidget(self.defaultfoil.no1.currentfoil)
        self.defaultfoil.no1.layout.addWidget(self.defaultfoil.no1.changebutton)
        self.defaultfoil.no1.setLayout(self.defaultfoil.no1.layout)

        self.defaultfoil.no2.layout = QtGui.QHBoxLayout()
        self.defaultfoil.no2.layout.addWidget(self.defaultfoil.no2.currentfoil)
        self.defaultfoil.no2.layout.addWidget(self.defaultfoil.no2.changebutton)
        self.defaultfoil.no2.setLayout(self.defaultfoil.no2.layout)

        self.defaultfoil.no3.layout = QtGui.QHBoxLayout()
        self.defaultfoil.no3.layout.addWidget(self.defaultfoil.no3.currentfoil)
        self.defaultfoil.no3.layout.addWidget(self.defaultfoil.no3.changebutton)
        self.defaultfoil.no3.setLayout(self.defaultfoil.no3.layout)

        self.defaultfoil.no4.layout = QtGui.QHBoxLayout()
        self.defaultfoil.no4.layout.addWidget(self.defaultfoil.no4.currentfoil)
        self.defaultfoil.no4.layout.addWidget(self.defaultfoil.no4.changebutton)
        self.defaultfoil.no4.setLayout(self.defaultfoil.no4.layout)

        self.defaultfoil.layout = QtGui.QVBoxLayout()
        self.defaultfoil.layout.addWidget(self.defaultfoil.no1)
        self.defaultfoil.layout.addWidget(self.defaultfoil.no2)
        self.defaultfoil.layout.addWidget(self.defaultfoil.no3)
        self.defaultfoil.layout.addWidget(self.defaultfoil.no4)

        self.defaultfoil.setLayout(self.defaultfoil.layout)

        self.dialog.layout = QtGui.QVBoxLayout()
        self.dialog.layout.addWidget(self.defaultdirectory)
        self.dialog.layout.addWidget(self.defaultfoil)
        self.dialog.setLayout(self.dialog.layout)

        self.dialog.connect(self.defaultdirectory.changebutton,QtCore.SIGNAL('clicked()'),change_dir)
        self.dialog.connect(self.defaultfoil.no1.changebutton,QtCore.SIGNAL('clicked()'),change_foil_no1)
        self.dialog.connect(self.defaultfoil.no2.changebutton,QtCore.SIGNAL('clicked()'),change_foil_no2)
        self.dialog.connect(self.defaultfoil.no3.changebutton,QtCore.SIGNAL('clicked()'),change_foil_no3)
        self.dialog.connect(self.defaultfoil.no4.changebutton,QtCore.SIGNAL('clicked()'),change_foil_no4)

class RangeChaneWidget(QtGui.QDialog):
    def __init__(self,parent = None):
        QtGui.QDialog.__init__(self, parent = parent)
        self.setWindowTitle(u"遺伝子係数設定")

        global coe_range,coe_start
        self.setModal(1)

        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)


        self.coe1 = QtGui.QGroupBox(u"第1翼型混合係数範囲",parent = self)
        self.coe1.setFont(font)
        self.coe1.stt_label = QtGui.QLabel(u"最小値",parent = self.coe1)
        self.coe1.stt_edit = QtGui.QLineEdit(parent = self.coe1)
        self.coe1.stt_edit.setFixedWidth(45)
        self.coe1.range_label = QtGui.QLabel(u"    最大値")
        self.coe1.range_edit = QtGui.QLineEdit(parent = self.coe1)
        self.coe1.range_edit.setFixedWidth(45)
        self.coe1.layout = QtGui.QHBoxLayout()
        self.coe1.layout.addWidget(self.coe1.stt_label)
        self.coe1.layout.addWidget(self.coe1.stt_edit)
        self.coe1.layout.addWidget(self.coe1.range_label)
        self.coe1.layout.addWidget(self.coe1.range_edit)
        self.coe1.setLayout(self.coe1.layout)

        self.coe2 = QtGui.QGroupBox(u"第2翼型混合係数範囲",parent = self)
        self.coe2.stt_label = QtGui.QLabel(u"最小値",parent = self.coe2)
        self.coe2.stt_edit = QtGui.QLineEdit(parent = self.coe2)
        self.coe2.stt_edit.setFixedWidth(45)
        self.coe2.range_label = QtGui.QLabel(u"    最大値")
        self.coe2.range_edit = QtGui.QLineEdit(parent = self.coe2)
        self.coe2.range_edit.setFixedWidth(45)
        self.coe2.layout = QtGui.QHBoxLayout()
        self.coe2.layout.addWidget(self.coe2.stt_label)
        self.coe2.layout.addWidget(self.coe2.stt_edit)
        self.coe2.layout.addWidget(self.coe2.range_label)
        self.coe2.layout.addWidget(self.coe2.range_edit)
        self.coe2.setLayout(self.coe2.layout)

        self.coe3 = QtGui.QGroupBox(u"第3翼型混合係数範囲",parent = self)
        self.coe3.stt_label = QtGui.QLabel(u"最小値",parent = self.coe3)
        self.coe3.stt_edit = QtGui.QLineEdit(parent = self.coe3)
        self.coe3.stt_edit.setFixedWidth(45)
        self.coe3.range_label = QtGui.QLabel(u"    最大値")
        self.coe3.range_edit = QtGui.QLineEdit(parent = self.coe3)
        self.coe3.range_edit.setFixedWidth(45)
        self.coe3.layout = QtGui.QHBoxLayout()
        self.coe3.layout.addWidget(self.coe3.stt_label)
        self.coe3.layout.addWidget(self.coe3.stt_edit)
        self.coe3.layout.addWidget(self.coe3.range_label)
        self.coe3.layout.addWidget(self.coe3.range_edit)
        self.coe3.setLayout(self.coe3.layout)

        self.coe4 = QtGui.QGroupBox(u"第4翼型混合係数範囲",parent = self)
        self.coe4.stt_label = QtGui.QLabel(u"最小値",parent = self.coe4)
        self.coe4.stt_edit = QtGui.QLineEdit(parent = self.coe4)
        self.coe4.stt_edit.setFixedWidth(45)
        self.coe4.range_label = QtGui.QLabel(u"    最大値")
        self.coe4.range_edit = QtGui.QLineEdit(parent = self.coe4)
        self.coe4.range_edit.setFixedWidth(45)
        self.coe4.layout = QtGui.QHBoxLayout()
        self.coe4.layout.addWidget(self.coe4.stt_label)
        self.coe4.layout.addWidget(self.coe4.stt_edit)
        self.coe4.layout.addWidget(self.coe4.range_label)
        self.coe4.layout.addWidget(self.coe4.range_edit)
        self.coe4.setLayout(self.coe4.layout)

        self.coe5 = QtGui.QGroupBox(u"追加キャンバ 最大キャンバy座標",parent = self)
        self.coe5.stt_label = QtGui.QLabel(u"最小値",parent = self.coe5)
        self.coe5.stt_edit = QtGui.QLineEdit(parent = self.coe5)
        self.coe5.stt_edit.setFixedWidth(45)
        self.coe5.range_label = QtGui.QLabel(u"    最大値")
        self.coe5.range_edit = QtGui.QLineEdit(parent = self.coe5)
        self.coe5.range_edit.setFixedWidth(45)
        self.coe5.layout = QtGui.QHBoxLayout()
        self.coe5.layout.addWidget(self.coe5.stt_label)
        self.coe5.layout.addWidget(self.coe5.stt_edit)
        self.coe5.layout.addWidget(self.coe5.range_label)
        self.coe5.layout.addWidget(self.coe5.range_edit)
        self.coe5.setLayout(self.coe5.layout)

        self.coe6 = QtGui.QGroupBox(u"追加キャンバ 最大キャンバx座標",parent = self)
        self.coe6.stt_label = QtGui.QLabel(u"最小値",parent = self.coe6)
        self.coe6.stt_edit = QtGui.QLineEdit(parent = self.coe6)
        self.coe6.stt_edit.setFixedWidth(45)
        self.coe6.range_label = QtGui.QLabel(u"    最大値")
        self.coe6.range_edit = QtGui.QLineEdit(parent = self.coe6)
        self.coe6.range_edit.setFixedWidth(45)
        self.coe6.layout = QtGui.QHBoxLayout()
        self.coe6.layout.addWidget(self.coe6.stt_label)
        self.coe6.layout.addWidget(self.coe6.stt_edit)
        self.coe6.layout.addWidget(self.coe6.range_label)
        self.coe6.layout.addWidget(self.coe6.range_edit)
        self.coe6.setLayout(self.coe6.layout)

        self.coe7 = QtGui.QGroupBox(u"追加キャンバ 後縁角度[deg]",parent = self)
        self.coe7.stt_label = QtGui.QLabel(u"最小値",parent = self.coe7)
        self.coe7.stt_edit = QtGui.QLineEdit(parent = self.coe7)
        self.coe7.stt_edit.setFixedWidth(45)
        self.coe7.range_label = QtGui.QLabel(u"    最大値")
        self.coe7.range_edit = QtGui.QLineEdit(parent = self.coe7)
        self.coe7.range_edit.setFixedWidth(45)
        self.coe7.layout = QtGui.QHBoxLayout()
        self.coe7.layout.addWidget(self.coe7.stt_label)
        self.coe7.layout.addWidget(self.coe7.stt_edit)
        self.coe7.layout.addWidget(self.coe7.range_label)
        self.coe7.layout.addWidget(self.coe7.range_edit)
        self.coe7.setLayout(self.coe7.layout)

        self.coe8 = QtGui.QGroupBox(u"翼厚係数",parent = self)
        self.coe8.stt_label = QtGui.QLabel(u"最小値",parent = self.coe8)
        self.coe8.stt_edit = QtGui.QLineEdit(parent = self.coe8)
        self.coe8.stt_edit.setFixedWidth(45)
        self.coe8.range_label = QtGui.QLabel(u"    最大値")
        self.coe8.range_edit = QtGui.QLineEdit(parent = self.coe8)
        self.coe8.range_edit.setFixedWidth(45)
        self.coe8.layout = QtGui.QHBoxLayout()
        self.coe8.layout.addWidget(self.coe8.stt_label)
        self.coe8.layout.addWidget(self.coe8.stt_edit)
        self.coe8.layout.addWidget(self.coe8.range_label)
        self.coe8.layout.addWidget(self.coe8.range_edit)
        self.coe8.setLayout(self.coe8.layout)

        self.coe9 = QtGui.QGroupBox(u"シェアリング",parent = self)
        self.coe9.label = QtGui.QLabel(u"　シェアリング半径   ",parent = self.coe9)
        self.coe9.edit = QtGui.QLineEdit(parent = self.coe9)
        self.coe9.edit.setFixedWidth(45)

        self.coe9.layout = QtGui.QHBoxLayout()
        self.coe9.layout.addWidget(self.coe9.label)
        self.coe9.layout.addWidget(self.coe9.edit)
        self.coe9.setLayout(self.coe9.layout)

        self.buttuns = QtGui.QWidget(parent = self)
        self.buttuns.done    = QtGui.QPushButton(u"適用")
        self.buttuns.cancel  = QtGui.QPushButton(u"キャンセル")
        self.buttuns.default = QtGui.QPushButton(u"初期設定")

        self.buttuns.layout = QtGui.QHBoxLayout()
        self.buttuns.layout.addStretch(1)
        self.buttuns.layout.addWidget(self.buttuns.done)
        self.buttuns.layout.addWidget(self.buttuns.cancel)
        self.buttuns.layout.addWidget(self.buttuns.default)
        self.buttuns.setLayout(self.buttuns.layout)

        #値のセット
        self.read_rangefile()
        self.coe1.stt_edit.setText("{coe1s}".format(coe1s   = round(coe_start[0],4)))
        self.coe1.range_edit.setText("{coe1r}".format(coe1r = round(coe_range[0]+coe_start[0],4)))
        self.coe2.stt_edit.setText("{coe2s}".format(coe2s   = round(coe_start[1],4)))
        self.coe2.range_edit.setText("{coe2r}".format(coe2r = round(coe_range[1]+coe_start[1],4)))
        self.coe3.stt_edit.setText("{coe3s}".format(coe3s   = round(coe_start[2],4)))
        self.coe3.range_edit.setText("{coe3r}".format(coe3r = round(coe_range[2]+coe_start[2],4)))
        self.coe4.stt_edit.setText("{coe4s}".format(coe4s   = round(coe_start[3],4)))
        self.coe4.range_edit.setText("{coe4r}".format(coe4r = round(coe_range[3]+coe_start[3],4)))
        self.coe5.stt_edit.setText("{coe5s}".format(coe5s   = round(coe_start[4],4)))
        self.coe5.range_edit.setText("{coe5r}".format(coe5r = round(coe_range[4]+coe_start[4],4)))
        self.coe6.stt_edit.setText("{coe6s}".format(coe6s   = round(coe_start[5],4)))
        self.coe6.range_edit.setText("{coe6r}".format(coe6r = round(coe_range[5]+coe_start[5],4)))
        self.coe7.stt_edit.setText("{coe7s}".format(coe7s   = round(coe_start[6],4)))
        self.coe7.range_edit.setText("{coe7r}".format(coe7r = round(coe_range[6]+coe_start[6],4)))
        self.coe8.stt_edit.setText("{coe8s}".format(coe8s   = round(coe_start[7],4)))
        self.coe8.range_edit.setText("{coe8r}".format(coe8r = round(coe_range[7]+coe_start[7],4)))
        self.coe9.edit.setText("{coe9}".format(coe9 = round(coe_range[8],4)))
        self.write_rangefile()




        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.coe1)
        self.layout.addWidget(self.coe2)
        self.layout.addWidget(self.coe3)
        self.layout.addWidget(self.coe4)
        self.layout.addWidget(self.coe5)
        self.layout.addWidget(self.coe6)
        self.layout.addWidget(self.coe7)
        self.layout.addWidget(self.coe8)
        self.layout.addWidget(self.coe9)
        self.layout.addWidget(self.buttuns)
        self.setLayout(self.layout)

        self.connect(self.buttuns.done,QtCore.SIGNAL('clicked()'),self.done)
        self.connect(self.buttuns.default,QtCore.SIGNAL('clicked()'),self.default)
        self.connect(self.buttuns.cancel,QtCore.SIGNAL('clicked()'),self.cancel)
        self.buttuns.done.setAutoDefault(True)


    def read_rangefile(self):
        try:
            rfile = numpy.loadtxt("defr.ini",delimiter =",")
            global coe_range,coe_start
            for i in range(9):
                coe_range[i] = round(rfile[i][1],4)
                coe_start[i] = round(rfile[i][0],4)
        except:
            #             No1   No2   No3   No4   zc     xc     alphaTe  thn sharing
            coe_range = [ 2.0,  2.0,  2.0,  2.0,  0.030, 0.40,  6.0,     1.4, 0.025]
            coe_start = [-1.0, -1.0, -1.0, -1.0, -0.015, 0.20, -3.0,     0.6, 0.025]



    def write_rangefile(self):
        global coe_range,coe_start
        #値の読込
        coe_range[0] = round(float(self.coe1.range_edit.text())-float(self.coe1.stt_edit.text()),4)
        coe_start[0] = round(float(self.coe1.stt_edit.text()),4)
        coe_range[1] = round(float(self.coe2.range_edit.text())-float(self.coe2.stt_edit.text()),4)
        coe_start[1] = round(float(self.coe2.stt_edit.text()),4)
        coe_range[2] = round(float(self.coe3.range_edit.text())-float(self.coe3.stt_edit.text()),4)
        coe_start[2] = round(float(self.coe3.stt_edit.text()),4)
        coe_range[3] = round(float(self.coe4.range_edit.text())-float(self.coe4.stt_edit.text()),4)
        coe_start[3] = round(float(self.coe4.stt_edit.text()),4)
        coe_range[4] = round(float(self.coe5.range_edit.text())-float(self.coe5.stt_edit.text()),4)
        coe_start[4] = round(float(self.coe5.stt_edit.text()),4)
        coe_range[5] = round(float(self.coe6.range_edit.text())-float(self.coe6.stt_edit.text()),4)
        coe_start[5] = round(float(self.coe6.stt_edit.text()),4)
        coe_range[6] = round(float(self.coe7.range_edit.text())-float(self.coe7.stt_edit.text()),4)
        coe_start[6] = round(float(self.coe7.stt_edit.text()),4)
        coe_range[7] = round(float(self.coe8.range_edit.text())-float(self.coe8.stt_edit.text()),4)
        coe_start[7] = round(float(self.coe8.stt_edit.text()),4)
        coe_range[8] = round(float(self.coe9.edit.text()),4)
        coe_start[8] = round(float(self.coe9.edit.text()),4)


        #値の書き込み
        fid = open("defr.ini",'w')
        writecsv = csv.writer(fid,lineterminator = "\n")
        for i in range(9):
            writecsv.writerow([round(coe_start[i],4),round(coe_range[i],4)])
        fid.close()

    def closeEvent(self, event):
        self.read_rangefile()
        event.accept()


    def done(self):
        self.write_rangefile()
        self.read_rangefile()
        self.close()
    def cancel(self):
        self.read_rangefile()
        self.close()
    def default(self):
        #             No1   No2   No3   No4   zc     xc     alphaTe  thn  sharing
        coe_range = [ 2.0,  2.0,  2.0,  2.0,  0.030, 0.40,  6.0,     1.4, 0.025]
        coe_start = [-1.0, -1.0, -1.0, -1.0, -0.015, 0.20, -3.0,     0.6, 0.025]
        self.coe1.stt_edit.setText("{coe1s}".format(coe1s   = round(coe_start[0],4)))
        self.coe1.range_edit.setText("{coe1r}".format(coe1r = round(coe_range[0]+coe_start[0],4)))
        self.coe2.stt_edit.setText("{coe2s}".format(coe2s   = round(coe_start[1],4)))
        self.coe2.range_edit.setText("{coe2r}".format(coe2r = round(coe_range[1]+coe_start[1],4)))
        self.coe3.stt_edit.setText("{coe3s}".format(coe3s   = round(coe_start[2],4)))
        self.coe3.range_edit.setText("{coe3r}".format(coe3r = round(coe_range[2]+coe_start[2],4)))
        self.coe4.stt_edit.setText("{coe4s}".format(coe4s   = round(coe_start[3],4)))
        self.coe4.range_edit.setText("{coe4r}".format(coe4r = round(coe_range[3]+coe_start[3],4)))
        self.coe5.stt_edit.setText("{coe5s}".format(coe5s   = round(coe_start[4],4)))
        self.coe5.range_edit.setText("{coe5r}".format(coe5r = round(coe_range[4]+coe_start[4],4)))
        self.coe6.stt_edit.setText("{coe6s}".format(coe6s   = round(coe_start[5],4)))
        self.coe6.range_edit.setText("{coe6r}".format(coe6r = round(coe_range[5]+coe_start[5],4)))
        self.coe7.stt_edit.setText("{coe7s}".format(coe7s   = round(coe_start[6],4)))
        self.coe7.range_edit.setText("{coe7r}".format(coe7r = round(coe_range[6]+coe_start[6],4)))
        self.coe8.stt_edit.setText("{coe8s}".format(coe8s   = round(coe_start[7],4)))
        self.coe8.range_edit.setText("{coe8r}".format(coe8r = round(coe_range[7]+coe_start[7],4)))
        self.coe9.edit.setText("{coe9r}".format(coe9r = round(coe_range[8],4)))
        self.write_rangefile()


def main():
    def update_showcoe():
        basefoilpanel.acamb.showfoil.update_figure_mult(ga.x[0:99], ga.top_addcamber[0:99])
        #係数値の提示
        basefoilpanel.no1.coe_label.setText(u"混合係数 : {coe}".format(coe = round(ga.top_coefficient[0],6)))
        basefoilpanel.no2.coe_label.setText(u"混合係数 : {coe}".format(coe = round(ga.top_coefficient[1],6)))
        basefoilpanel.no3.coe_label.setText(u"混合係数 : {coe}".format(coe = round(ga.top_coefficient[2],6)))
        basefoilpanel.no4.coe_label.setText(u"混合係数 : {coe}".format(coe = round(ga.top_coefficient[3],6)))
        basefoilpanel.acamb.thnlabel.setText(u"翼厚係数 : {coe}".format(coe =round(ga.top_coefficient[7],4)))


    def exeGA():
        try:
            os.remove("a0_pwrt.dat")
        except:
            pass
        if not basefoilpanel.no1.showfoil.filename or not basefoilpanel.no2.showfoil.filename or not basefoilpanel.no3.showfoil.filename or not basefoilpanel.no4.showfoil.filename :
            QtGui.QMessageBox.warning(None,u"翼型がありません", u"基準翼型を選択して下さい\nデフォルト設定を行っていないのであれば、\nOptionタブより設定して下さい",
                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            titleexeprogress.exebutton.setText(u"計算")
        else:
            titleexeprogress.stopbutton.setDisabled(0)
            max_generation = int(titleexeprogress.inputgeneration.text())
            global n_sample
            n_sample = int(titleexeprogress.inputindno.text())

            if ga.generation < max_generation:
                while ga.generation < max_generation:
                    qApp.processEvents()
                    if ga.run !=0 and ga.run !=2 :
                        break
                    ga.generation += 1


                    if ga.generation == 1:
                        titleexeprogress.generation.setText(u"  世代 : 0 / ")
                        n_sample = int(titleexeprogress.inputindno.text())
                        titleexeprogress.inputindno.setDisabled(1)

                        ga.getFoilChord(basefoilpanel)
                        ga.defineFoil()
                        ga.default_gene()
                        ga.gene2coeficient()
                        ga.coeficient2foil()
                        ga.run = 2
                        ga.exeXFoil(qApp,titleexeprogress,input_widget)

                        if ga.run == 0 or ga.run == 2:
                            ga.evaluete_cross(input_widget,ga.generation,titleexeprogress.savedonelabel)
                            if numpy.min(ga.Fcon) < 0:
                                QtGui.QMessageBox.warning(None,u"Fcon error", u"評価関数の値が負になっています。評価関数の係数を調節して下さい",
                                            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                                stopGA()
                            else:
                                cfoil_widget.replot(ga,ga.maxFconNo)
                                dataplotwidget.update_dataplot(ga,ga.generation)
                                update_showcoe()
                    else:
                        titleexeprogress.generation.setText(u"世代 : {fgene} / ".format(fgene = ga.generation-1))
                        ga.gene2coeficient()
                        ga.coeficient2foil()
                        ga.run = 2
                        ga.exeXFoil(qApp,titleexeprogress,input_widget)
                        if ga.run == 0 or ga.run == 2:
                            ga.evaluete_cross(input_widget,ga.generation,titleexeprogress.savedonelabel)
                            cfoil_widget.replot(ga,ga.maxFconNo)
                            dataplotwidget.update_dataplot(ga,ga.generation)
                            update_showcoe()

                    if ga.run ==0 or ga.run ==2 :
                        cfoil_widget.combobox.clear()
                        for combo_n in range(ga.generation,0,-1):
                            cfoil_widget.combobox.addItem(str(combo_n))
                    max_generation = int(titleexeprogress.inputgeneration.text())
                    if ga.generation == max_generation:
                        titleexeprogress.generation.setText(u"世代 : {fgene} / ".format(fgene = ga.generation))
                        titleexeprogress.stopbutton.setText(u"続行")
                        ga.run = 1
                        ga.generation += 1
                        cfoil_widget.rollbackbutton.setEnabled(True)
                        cfoil_widget.outputbutton.setEnabled(True)
                        cfoil_widget.combobox.setEnabled(True)
            else:
                ga.generation += 1





    def startGA():
        ret = QtGui.QMessageBox.question(None,u"GA　実行", u"世代:0から最適化計算を実行します\nよろしいですか？",
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No ,QtGui.QMessageBox.Yes)
        if ret == QtGui.QMessageBox.Yes:
            ga.generation = 0
            ga.run = 0
            ga.save_top = [0]
            ga.save_topValue = [0]
            titleexeprogress.exebutton.setText(u"再計算")
            font = QtGui.QFont()
            font.setPointSize(12)
            titleexeprogress.exebutton.setFont(font)

            titleexeprogress.stopbutton.setText(u"一時停止")
            titleexeprogress.stopbutton.setFont(font)
            cfoil_widget.rollbackbutton.setEnabled(False)
            cfoil_widget.outputbutton.setEnabled(False)
            cfoil_widget.combobox.setEnabled(False)
            cfoil_widget.combobox.clear()
            exeGA()

    def stopGA():
        if ga.run == 0 or ga.run == 2 :
            ga.run = 1
            titleexeprogress.stopbutton.setText(u"続行")
            cfoil_widget.rollbackbutton.setEnabled(True)
            cfoil_widget.outputbutton.setEnabled(True)
            cfoil_widget.combobox.setEnabled(True)
        elif ga.generation < int(titleexeprogress.inputgeneration.text())+1:
            ga.run = 2
            ga.generation -= 1
            titleexeprogress.stopbutton.setText(u"一時停止")
            cfoil_widget.rollbackbutton.setEnabled(False)
            cfoil_widget.outputbutton.setEnabled(False)
            cfoil_widget.combobox.setEnabled(False)
            exeGA()

        else:
            QtGui.QMessageBox.warning(None,u"計算が一時停止されました", u"世代が上限に達しています",
                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)



    def quitGA():
        ga.run = 1


    def newproject():
        #a0_pwrt.datを削除
        try:
            os.remove("a0_pwrt.dat")
        except:
            pass
        basefoilpanel.no1.showfoil.compute_initial_figure2(default.default_no1)
        basefoilpanel.no1.setTitle(u"第1翼型 - {foilname}".format(foilname = os.path.basename(basefoilpanel.no1.showfoil.filename)))
        basefoilpanel.no2.showfoil.compute_initial_figure2(default.default_no2)
        basefoilpanel.no2.setTitle(u"第2翼型 - {foilname}".format(foilname = os.path.basename(basefoilpanel.no2.showfoil.filename)))
        basefoilpanel.no3.showfoil.compute_initial_figure2(default.default_no3)
        basefoilpanel.no3.setTitle(u"第3翼型 - {foilname}".format(foilname = os.path.basename(basefoilpanel.no3.showfoil.filename)))
        basefoilpanel.no4.showfoil.compute_initial_figure2(default.default_no4)
        basefoilpanel.no4.setTitle(u"第4翼型 - {foilname}".format(foilname = os.path.basename(basefoilpanel.no4.showfoil.filename)))

        ga.save_top = [0]
        ga.save_topValue = [0]
        ga.run = 0

        titleexeprogress.exebutton.setText(u"計算")
        titleexeprogress.stopbutton.setText(u"一時停止")

        input_widget.inputwidget.inputalpha.setText('4')
        input_widget.inputwidget.inputCL.setText('1.2')
        input_widget.inputwidget.inputRe.setText('500000')
        input_widget.inputwidget.inputthn.setText('11')
        input_widget.inputwidget.inputthnpos.setText('36')
        input_widget.inputwidget.inputminCd.setText('65')

        input_widget.inputevafunc.P1.setText('1')
        input_widget.inputevafunc.P2.setText('0')
        input_widget.inputevafunc.P3.setText('5')
        input_widget.inputevafunc.P4.setText('10')

        titleexeprogress.inputindno.setDisabled(0)
        titleexeprogress.stopbutton.setDisabled(1)
        input_widget.inputwidget.inputalpha.setDisabled(0)
        cfoil_widget.rollbackbutton.setEnabled(False)
        cfoil_widget.outputbutton.setEnabled(False)
        cfoil_widget.combobox.setEnabled(False)

        titleexeprogress.progressbar.reset()
        cfoil_widget.CLlabel.setText(u"揚力係数CL : {CL}    抗力係数Cd(*10000) : {Cd}    揚抗比CL/Cd : {CLCd}    モーメント係数Cm : {Cm}     翼厚 : {thn:4}".format(CL = "NaN", Cd = "NaN", CLCd = "NaN",Cm = "Nan", thn = "NaN"))
        titleexeprogress.progressbar.reset()
        global projectname
        projectname = ""
        main_window.setWindowTitle("XGAG")
        titleexeprogress.savedonelabel.setText(u"新規プロジェクトを開始しました")


    def rollback():
        ret = QtGui.QMessageBox.question(None,u"巻き戻し", u"世代:{generation}を最も優れた翼型として登録します\n(評価関数が最大値をとった翼型は登録され、毎世代投入されます)\nよろしいですか？".format(generation = int(cfoil_widget.combobox.currentText())),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
        if ret == QtGui.QMessageBox.Yes:
            rollbacgeneration = int(cfoil_widget.combobox.currentText())
            ga.save_top = copy.deepcopy(ga.history_top[rollbacgeneration-1])
            ga.save_topValue = copy.deepcopy(ga.history_topValue[rollbacgeneration-1])
            ga.gene2[n_sample-1] = copy.deepcopy(ga.save_top)

    def expot_foil():
        export.gene2foil(ga,int(cfoil_widget.combobox.currentText()))
        export.dialog(cfoil_widget,input_widget,default)
        if export.exfail == 0:
            titleexeprogress.savedonelabel.setText(u"世代:{gene}の翼型を出力しました".format(gene = cfoil_widget.combobox.currentText()))
        else:
            titleexeprogress.savedonelabel.setText(u"翼型出力を中止しました")

    def save_file():
        fid = open(projectname,"w")
        writecsv = csv.writer(fid,lineterminator = "\n")
        writecsv.writerow([u"#! XGAG 状況保存"])
        writecsv.writerows(ga.gene2)

        writecsv = csv.writer(fid,lineterminator = "\n")
        writecsv.writerow(["---"])
        writecsv.writerow(ga.save_top)
        writecsv.writerow([str(ga.save_topValue)])
        writecsv.writerow([str(int(titleexeprogress.inputgeneration.text()))])

        writecsv.writerow(["---"])

        for history_Fcon in numpy.ndarray.tolist(ga.history_Fcon):
            writecsv.writerow([str(history_Fcon)])
        writecsv.writerow(["---"])

        for history_CL in numpy.ndarray.tolist(ga.history_CL):
            writecsv.writerow([str(history_CL)])
        writecsv.writerow(["---"])

        for history_Cd in numpy.ndarray.tolist(ga.history_Cd):
            writecsv.writerow([str(history_Cd)])
        writecsv.writerow(["---"])

        for history_Cm in numpy.ndarray.tolist(ga.history_Cm):
            writecsv.writerow([str(history_Cm)])
        writecsv.writerow(["---"])

        for history_CLCD in numpy.ndarray.tolist(ga.history_CLCD):
            writecsv.writerow([str(history_CLCD)])
        writecsv.writerow(["---"])

        for history_thn in numpy.ndarray.tolist(ga.history_thn):
            writecsv.writerow([str(history_thn)])
        writecsv.writerow(["---"])

        for i in range(ga.generation-1):
            writecsv.writerow([str(ga.history_topValue[i])])
        writecsv.writerow(["---"])

        for i in range(ga.generation-1):
            writecsv.writerow(ga.history_top[i])
        writecsv.writerow(["---"])

        writecsv.writerow([basefoilpanel.no1.showfoil.filename])
        writecsv.writerow([basefoilpanel.no2.showfoil.filename])
        writecsv.writerow([basefoilpanel.no3.showfoil.filename])
        writecsv.writerow([basefoilpanel.no4.showfoil.filename])

        writecsv.writerow(["---"])

        #generation
        writecsv.writerow([str(ga.generation)])
        writecsv.writerow([str(n_sample)])

        #評価関数
        writecsv.writerow([str(ga.pfCd)])
        writecsv.writerow([str(ga.pfCm)])
        writecsv.writerow([str(ga.pfCL)])
        writecsv.writerow([str(ga.pfthn)])

        #評価関数
        writecsv.writerow([input_widget.inputwidget.inputalpha.text()])
        writecsv.writerow([input_widget.inputwidget.inputRe.text()])
        writecsv.writerow([input_widget.inputwidget.inputCL.text()])
        writecsv.writerow([input_widget.inputwidget.inputthn.text()])
        writecsv.writerow([input_widget.inputwidget.inputthnpos.text()])
        writecsv.writerow([input_widget.inputwidget.inputminCd.text()])
        writecsv.writerow(["---"])

        #sortedlist
        numpy.savetxt("numpyout.buff",ga.sortedlist,delimiter = ",",fmt="%.9f")
        f = open("numpyout.buff","r")
        csv_buff = csv.reader(f,delimiter = ',')
        csv_writebuff = []
        for data in csv_buff:
            csv_writebuff.append(data)
        f.close()
        os.remove("numpyout.buff")

        for iter_sort in csv_writebuff:
            writecsv.writerow(iter_sort)
        writecsv.writerow(["---"])

        #翼型
        foiloutbuff = numpy.vstack([cfoil_widget.cfw.Fx,cfoil_widget.cfw.Fy])
        numpy.savetxt("numpyout.buff",foiloutbuff,delimiter = ",",fmt="%.9f")
        f = open("numpyout.buff","r")
        csv_buff = csv.reader(f,delimiter = ',')
        csv_writebuff = []
        for data in csv_buff:
            csv_writebuff.append(data)
        f.close()
        os.remove("numpyout.buff")
        for iter_sort in csv_writebuff:
            writecsv.writerow(iter_sort)
        writecsv.writerow(["---"])

        #history
        historyoutbuff = numpy.vstack([ga.history_Fcon,ga.history_CL,ga.history_Cd,ga.history_Cm,ga.history_CLCD,ga.history_thn,ga.history_generation])
        numpy.savetxt("numpyout.buff",historyoutbuff,delimiter = ",",fmt="%.9f")
        f = open("numpyout.buff","r")
        csv_buff = csv.reader(f,delimiter = ',')
        csv_writebuff = []
        for data in csv_buff:
            csv_writebuff.append(data)
        f.close()
        os.remove("numpyout.buff")
        for iter_sort in csv_writebuff:
            writecsv.writerow(iter_sort)
        writecsv.writerow(["---"])

        fid.close()
        titleexeprogress.savedonelabel.setText(u"セーブが完了しました")
        main_window.setWindowTitle("XGAG -{projectname}".format(projectname = os.path.basename(projectname)))

    def open_file():
        #CSVリストの作成
        global projectname
        projectname= QtGui.QFileDialog.getOpenFileName(parent = None,caption = "open project" ,directory=os.path.join(default.foildirectory), filter="XGAG File(*.gag)")
        if projectname:
            fid = open(projectname)
            csv_openfile = csv.reader(fid,delimiter = ',')
            read_n = 0
            csv_allfile = []
            for data in csv_openfile:
                csv_allfile.append(data)
            fid.close()

            #リストよりgene抽出
            gene = []
            read_i = 1
            while 1:
                if csv_allfile[read_i] == ['---']:
                    break
                gene.append(csv_allfile[read_i])
                read_i += 1
            ga.gene2 = gene
            n_sample = numpy.shape(ga.gene2)[0]

            #リストよりsave_topおよびsave_topValue抽出
            read_i += 1
            ga.save_top =csv_allfile[read_i]
            read_i += 1
            ga.save_topValue = float(csv_allfile[read_i][0])
            read_i += 1
            titleexeprogress.inputgeneration.setText(csv_allfile[read_i][0])
            read_i += 1


            #history_Fcon
            read_i += 1
            history_Fcon_list = []
            while 1:
                if csv_allfile[read_i] == ['---']:
                    break
                history_Fcon_list.append(float(csv_allfile[read_i][0]))
                read_i += 1

            ga.history_Fcon = numpy.array(history_Fcon_list)
            read_i += 1

            #history_CL
            history_CL_list = []
            while 1:
                if csv_allfile[read_i] == ['---']:
                    break
                history_CL_list.append(float(csv_allfile[read_i][0]))
                read_i += 1

            ga.history_CL = numpy.array(history_CL_list)
            read_i += 1


            #history_Cd

            history_Cd_list = []
            while 1:
                if csv_allfile[read_i] == ['---']:
                    break
                history_Cd_list.append(float(csv_allfile[read_i][0]))
                read_i += 1

            ga.history_Cd = numpy.array(history_Cd_list)
            read_i += 1


            #history_CLCD
            history_Cm_list = []
            while 1:
                if csv_allfile[read_i] == ['---']:
                    break
                history_Cm_list.append(float(csv_allfile[read_i][0]))
                read_i += 1

            ga.history_Cm = numpy.array(history_Cm_list)
            read_i += 1



            #history_CLCD
            history_CLCD_list = []
            while 1:
                if csv_allfile[read_i] == ['---']:
                    break
                history_CLCD_list.append(float(csv_allfile[read_i][0]))
                read_i += 1

            ga.history_CLCD = numpy.array(history_CLCD_list)
            read_i += 1


            #history_thn
            history_thn_list = []
            while 1:
                if csv_allfile[read_i] == ['---']:
                    break
                history_thn_list.append(float(csv_allfile[read_i][0]))
                read_i += 1

            ga.history_thn = numpy.array(history_thn_list)
            read_i += 1


            #history_haistory_topval
            history_topValue_list = []
            while 1:
                if csv_allfile[read_i] == ['---']:
                    break
                history_topValue_list.append(float(csv_allfile[read_i][0]))
                read_i += 1

            ga.history_topValue = history_topValue_list
            read_i += 1


            history_top = []
            while 1:
                if csv_allfile[read_i] == ['---']:
                    break
                history_top.append(csv_allfile[read_i])
                read_i += 1

            ga.history_top = history_top
            read_i += 1

            #リストよりbasefail名抽出

            basefoilpanel.no1.showfoil.filename = csv_allfile[read_i][0]
            basefoilpanel.no1.showfoil.update_figure2()
            basefoilpanel.no1.setTitle(u"第1翼型 - {foilname}".format(foilname = os.path.basename(basefoilpanel.no1.showfoil.filename)))
            read_i += 1

            basefoilpanel.no2.showfoil.filename = csv_allfile[read_i][0]
            basefoilpanel.no2.showfoil.update_figure2()
            basefoilpanel.no2.setTitle(u"第2翼型 - {foilname}".format(foilname = os.path.basename(basefoilpanel.no2.showfoil.filename)))
            read_i += 1

            basefoilpanel.no3.showfoil.filename = csv_allfile[read_i][0]
            basefoilpanel.no3.showfoil.update_figure2()
            basefoilpanel.no3.setTitle(u"第3翼型 - {foilname}".format(foilname = os.path.basename(basefoilpanel.no3.showfoil.filename)))
            read_i += 1

            basefoilpanel.no4.showfoil.filename = csv_allfile[read_i][0]
            basefoilpanel.no4.showfoil.update_figure2()
            basefoilpanel.no4.setTitle(u"第4翼型 - {foilname}".format(foilname = os.path.basename(basefoilpanel.no4.showfoil.filename)))
            read_i += 1

            #リストより各設計パラメタ、評価関数 generation 抽出
            read_i += 1
            ga.generation = int(csv_allfile[read_i][0])
            titleexeprogress.generation.setText(u"世代 : {fgene} / ".format(fgene = ga.generation-1))
            read_i += 1
            n_sample = int(csv_allfile[read_i][0])

            #各設計パラメタおよびsortedlistの抽出
            read_i += 1
            input_widget.inputevafunc.P1.setText(csv_allfile[read_i][0])
            read_i += 1
            input_widget.inputevafunc.P2.setText(csv_allfile[read_i][0])
            read_i += 1
            input_widget.inputevafunc.P3.setText(csv_allfile[read_i][0])
            read_i += 1
            input_widget.inputevafunc.P4.setText(csv_allfile[read_i][0])

            ga.pfCd = float(input_widget.inputevafunc.P1.text())
            ga.pfCm = float(input_widget.inputevafunc.P2.text())
            ga.pfCL =float(input_widget.inputevafunc.P3.text())
            ga.pfthn =float(input_widget.inputevafunc.P4.text())

            read_i += 1
            input_widget.inputwidget.inputalpha.setText(csv_allfile[read_i][0])
            read_i += 1
            input_widget.inputwidget.inputRe.setText(csv_allfile[read_i][0])
            read_i += 1
            input_widget.inputwidget.inputCL.setText(csv_allfile[read_i][0])
            ga.CL_forplot = float(csv_allfile[read_i][0])
            read_i += 1
            input_widget.inputwidget.inputthn.setText(csv_allfile[read_i][0])
            ga.thn_forplot = float(csv_allfile[read_i][0])
            read_i += 1
            input_widget.inputwidget.inputthnpos.setText(csv_allfile[read_i][0])
            read_i += 1
            input_widget.inputwidget.inputminCd.setText(csv_allfile[read_i][0])



            read_i += 2
            input_array_buff = csv_allfile[read_i:read_i + n_sample]
            fid = open("inputsorted.buff","w")
            writecsv = csv.writer(fid,lineterminator = "\n")
            writecsv.writerows(input_array_buff)
            fid.close()
            ga.sortedlist = numpy.loadtxt("inputsorted.buff",delimiter = ",",ndmin = 2)
            os.remove("inputsorted.buff")

            read_i += n_sample+1
            input_array_buff = csv_allfile[read_i:read_i + 2]
            fid = open("inputbuff.buff","w")
            writecsv = csv.writer(fid,lineterminator = "\n")
            writecsv.writerows(input_array_buff)
            fid.close()
            foilbuff = numpy.loadtxt("inputbuff.buff",delimiter = ",",ndmin = 2)
            os.remove("inputbuff.buff")
            cfoil_widget.cfw.Fx = foilbuff[0,:]
            cfoil_widget.cfw.Fy = foilbuff[1,:]


            read_i += 3
            input_array_buff = csv_allfile[read_i:numpy.shape(csv_allfile)[0]-1]
            fid = open("inputbuff.buff","w")
            writecsv = csv.writer(fid,lineterminator = "\n")
            writecsv.writerows(input_array_buff)
            fid.close()
            historybuff = numpy.loadtxt("inputbuff.buff",delimiter = ",",ndmin = 2)
            os.remove("inputbuff.buff")
            ga.history_Fcon = historybuff[0,:]
            ga.history_CL   = historybuff[1,:]
            ga.history_Cd   = historybuff[2,:]
            ga.history_Cm   = historybuff[3,:]
            ga.history_CLCD = historybuff[4,:]
            ga.history_thn  = historybuff[5,:]
            ga.history_generation = historybuff[6,:]


            #dataplot を再描画する
            ga.CL_forplot = float(input_widget.inputwidget.inputCL.text())
            ga.thn_forplot = float(input_widget.inputwidget.inputthn.text())/100

            dataplotwidget.update_dataplot(ga,ga.generation)
            cfoil_widget.replot2(ga)

            #その他諸々の設定
            ga.run = 1
            titleexeprogress.stopbutton.setText(u"続行")
            titleexeprogress.exebutton.setText(u"再計算")
            titleexeprogress.stopbutton.setEnabled(True)
            titleexeprogress.progressbar.reset()
            cfoil_widget.rollbackbutton.setEnabled(True)
            cfoil_widget.outputbutton.setEnabled(True)
            cfoil_widget.combobox.setEnabled(True)

            ga.getFoilChord(basefoilpanel)
            ga.defineFoil()
            ga.run = 1
            titleexeprogress.inputindno.setDisabled(1)

            for combo_n in range(ga.generation-1,0,-1):
                cfoil_widget.combobox.addItem(str(combo_n))

            main_window.setWindowTitle("XGAG -{projectname}".format(projectname = os.path.basename(projectname)))
            titleexeprogress.savedonelabel.setText(u"ロードが完了しました")

    def about_XGAG():
        QtGui.QMessageBox.about(None,"About XGAG","".join(["<h2>XGAG 2.00</h2>",
                                               "<p>Copyright (C) 2013 Naoto Morita",
                                               "<br>Copyright (C) 2000 Mark Drela, Harold Youngren</br></p>",
                                               "<p>Special thanks to : Masanao Matsunaga, Satoshi Utada, Daiki Adachi, Koichi Tsumori, bambino_del_uccello,"
                                               "   Kenji Takei, Kosuke Okabe, Ryosuke Ikeda, Tetsuya Okano, Tomonari Sato, Masahiro Ota, meka, Yuji Fukami"
                                               "<p>Icon : "
                                               "<p>XGAG is without any warranty. This program has been developed excusively for the design of airfoil. Any other usage is strongly disapproved.</p>"
                                               "<p>XGAG distributed under the GNU General Public Licence</p>"]))

    def save_as():
        global projectname
        projectname = QtGui.QFileDialog.getSaveFileName(None, caption = "project name",directory = os.path.join(default.foildirectory),filter = "XGAG File(*.gag)")
        if not projectname:
            pass
        elif ga.generation <= 1:
            main_window.setWindowTitle("XGAG -{projectname}".format(projectname = os.path.basename(projectname)))
        else:
            save_file()

    def save():
        global projectname
        if ga.generation <= 1 :
            projectname = QtGui.QFileDialog.getSaveFileName(None, caption = "project name",directory = os.path.join(default.foildirectory),filter = "XGAG File(*.gag)")
            main_window.setWindowTitle("XGAG -{projectname}".format(projectname = os.path.basename(projectname)))
        elif not projectname:
            save_as()
        else:
            save_file()

    def openif():
        if ga.run != 2:
            open_file()
        else:
            titleexeprogress.savedonelabel.setText(u"最適化をストップしてからオープンして下さい")

    def new():
        if ga.run != 2 :
            newproject()
        else:
            titleexeprogress.savedonelabel.setText(u"最適化をストップしてから新規プロジェクトを開始して下さい")

    qApp = QtGui.QApplication(sys.argv)


#インスタンスの作成
    #メインウィンドウ
    main_window=QtGui.QMainWindow()

    #デフォルト値読込
    default = Foils_Default_Change()
    default.read_init_file()
    default.change_dialog()

    #エクスポート用インスタンス
    export = Export_Filt_Foil()

    #メインウィンドウにそのまま貼り付けるウィジット
    main_panel = QtGui.QWidget()

#---------初期化のための再実行ここから
    #GA実行インスタンス
    ga = GeneteticAlgolithm()
    global projectname
    projectname = ""

    #変数レンジを設定するウィジット
    rangechangewidget = RangeChaneWidget(parent = None)

    #右側の翼型選択ウィジット
    basefoilpanel = BaseFoilWidget(default, parent = main_panel)

    #左側の側のデータ表示ウィジット
    input_data_panel = QtGui.QWidget()

    #データ表示ウィジットの中身
    input_widget = Inputtarget_Setbutton_Widget(parent = input_data_panel)
    cfoil_widget = CalclatedFoilWidget(default, ga, 0, parent = input_data_panel)
    #エキスポートボタン等を使えなくしておく
    cfoil_widget.rollbackbutton.setEnabled(False)
    cfoil_widget.outputbutton.setEnabled(False)
    cfoil_widget.combobox.setEnabled(False)
    dataplotwidget = DataPlotWidget(parent = input_data_panel)
    titleexeprogress = TitleExeStopProgressWidget(parent = input_data_panel)
    titleexeprogress.stopbutton.setDisabled(1)
    global n_sample
    n_sample = int(titleexeprogress.inputindno.text())
    #データ表示ウィジットのレイアウト
    input_data_panel_layput = QtGui.QVBoxLayout()
    input_data_panel_layput.addWidget(titleexeprogress)
    input_data_panel_layput.addWidget(input_widget.basecontener)
    input_data_panel_layput.addWidget(cfoil_widget.itgcfw)
    input_data_panel_layput.addWidget(dataplotwidget.main_widget)
    input_data_panel.setLayout(input_data_panel_layput)



#---------初期化のための再実行ここまで

    #メインパネルのレイアウト
    main_panel_layout = QtGui.QHBoxLayout()
    main_panel_layout.addWidget(input_data_panel)
    main_panel_layout.addWidget(basefoilpanel.basepanel)
    main_panel.setLayout(main_panel_layout)

    #メインウィンドウの設定
    main_window.setCentralWidget(main_panel)
    main_window.setWindowTitle("XGAG")
    main_window.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
    main_window.showMaximized()

    #メニューバーの作成
    menubar = main_window.menuBar()
    filemenu = menubar.addMenu(u"ファイル")
    file_new = filemenu.addAction(u"新規")
    file_new.setShortcut('Ctrl+N')
    file_open = filemenu.addAction(u"開く")
    file_open.setShortcut('Ctrl+O')
    file_save = filemenu.addAction(u"保存")
    file_save.setShortcut('Ctrl+S')
    file_saveas = filemenu.addAction(u"名前を付けて保存")
    main_window.connect(file_new,QtCore.SIGNAL('triggered()'),new)
    main_window.connect(file_save,QtCore.SIGNAL('triggered()'),save)
    main_window.connect(file_saveas,QtCore.SIGNAL('triggered()'),save_as)
    main_window.connect(file_open,QtCore.SIGNAL('triggered()'),openif)

    #ステータスバーにprogressを表示
    statusbar = QtGui.QStatusBar(main_window)
    statusbar.addWidget(titleexeprogress.progressbar)
    statusbar.addWidget(titleexeprogress.savedonelabel)
    main_window.setStatusBar(statusbar)

    optionmenu = menubar.addMenu(u"設定")
    defaultfoils = optionmenu.addAction(u"&既定翼型設定")
    defaultrange = optionmenu.addAction(u"&遺伝子係数設定")
    main_window.connect(defaultfoils,QtCore.SIGNAL('triggered()'),default.dialog.activateWindow)
    main_window.connect(defaultfoils,QtCore.SIGNAL('triggered()'),default.dialog.show)
    main_window.connect(defaultrange,QtCore.SIGNAL('triggered()'),rangechangewidget.activateWindow)
    main_window.connect(defaultrange,QtCore.SIGNAL('triggered()'),rangechangewidget.show)


    aboutmenu = menubar.addMenu("about")
    about_XGAGmenu = aboutmenu.addAction(u"XGAGについて")
    about_qt = aboutmenu.addAction(u"Qtについて")

    main_window.connect(about_qt,QtCore.SIGNAL('triggered()'),qApp.aboutQt)
    main_window.connect(about_XGAGmenu,QtCore.SIGNAL('triggered()'),about_XGAG)


    #a0_pwrt.datを削除
    try:
        os.remove("a0_pwrt.dat")
    except:
        pass

    #シグナルの設定
    titleexeprogress.connect(titleexeprogress.exebutton,QtCore.SIGNAL('clicked()'),startGA)
    titleexeprogress.connect(titleexeprogress.stopbutton,QtCore.SIGNAL('clicked()'),stopGA)
    cfoil_widget.connect(cfoil_widget.outputbutton,QtCore.SIGNAL('clicked()'),expot_foil)
    cfoil_widget.connect(cfoil_widget.rollbackbutton,QtCore.SIGNAL('clicked()'),rollback)

    qApp.connect(qApp,QtCore.SIGNAL("lastWindowClosed()"),quitGA)
    sys.exit(qApp.exec_())

if __name__ == '__main__':
    main()

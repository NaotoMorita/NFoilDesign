#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:衝撃波角β及び偏角θ、マッハ数を求めるプログラム
#
# Author:      NaotoMORITA
#
# Created:     09/04/2014
# Copyright:   (c) NaotoMORITA 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import numpy, csv,copy,warnings
import scipy.optimize as opt

import sys, os, copy
from PyQt4 import QtGui, QtCore

import matplotlib.backends.backend_qt4agg
import matplotlib.backends.backend_agg

class Dataplot(matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=3, dpi=50):
        self.fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis='both', which='major', labelsize=20)
        self.axes.hold(True)

        matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)

        matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg.updateGeometry(self)

    def drawplot(self,x,y,x2 = "None",y2 = "None",x3 = "None",y3 = "None",ylim = "None", xlabel = "None",ylabel = "None",legend = "None", aspect = "equal",hold = "true"):
            self.axes.plot(x,y)
            self.axes.hold(True)
            if x2 != "None":
                self.axes.plot(x2,y2)
            if x3 != "None":
                self.axes.plot(x3,y3,'r')
            if xlabel != "None":
                self.axes.set_xlabel(xlabel,fontsize = 20)
            if ylabel != "None":
                self.axes.set_ylabel(ylabel,fontsize = 20)
            if ylim !="None":
                self.axes.set_ylim(ylim)

            if legend != "None":
                self.axes.legend(legend,fontsize = 15, loc='upper left')
            if aspect =="equal":
                self.axes.set_aspect("equal")
            if hold == "false":
                self.axes.hold(False)




            self.draw()

class SettingWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QTabWidget.__init__(self, parent = parent)

        wantlabel = QtGui.QLabel(u"求めたいもの",parent = self)
        self.combo = QtGui.QComboBox(parent = self)
        self.combo.addItem(u"衝撃波角(deg)")
        self.combo.addItem(u"偏角(deg)")
        self.combo.addItem(u"マッハ数")

        self.exebutton = QtGui.QPushButton(u"計算")

        thetalabel = QtGui.QLabel(u"  偏角(deg)： ")
        betalabel = QtGui.QLabel(u"  衝撃波角(deg)： ")
        machlabel = QtGui.QLabel(u"  マッハ数: ")
        self.thetaedit = QtGui.QLineEdit()
        self.thetaedit.setFixedWidth(50)
        self.betaedit  = QtGui.QLineEdit()
        self.betaedit.setFixedWidth(50)
        self.machedit  = QtGui.QLineEdit()
        self.machedit.setFixedWidth(50)

        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(wantlabel)
        self.layout.addWidget(self.combo)
        self.layout.addStretch(1)
        self.layout.addWidget(betalabel)
        self.layout.addWidget(self.betaedit)
        self.layout.addWidget(thetalabel)
        self.layout.addWidget(self.thetaedit)
        self.layout.addWidget(machlabel)
        self.layout.addWidget(self.machedit)
        self.layout.addWidget(self.exebutton)
        self.setLayout(self.layout)

class Solve():
    def __init__(self):
        self.mach = 6
        self.theta = 0.1
        self.beta = 0.1
        self.kappa = 1.4
        self.exceptflag = 0

    def readedit(self,settingwidget):
        self.want = settingwidget.combo.currentIndex()
        print(self.want)
        if self.want == 0:
            try:
                self.theta = float(settingwidget.thetaedit.text()) / 180 * numpy.pi
                self.mach = float(settingwidget.machedit.text())
            except:
                QtGui.QMessageBox.warning(None,"Error",u"値の読込に失敗しました。\n偏角とマッハ数が正しく入力されているか確認して下さい")
                self.exceptflag = 1
        elif self.want == 1:
            try:
                self.beta = float(settingwidget.betaedit.text()) / 180 * numpy.pi
                self.mach = float(settingwidget.machedit.text())
            except:
                QtGui.QMessageBox.warning(None,"Error",u"値の読込に失敗しました。\n衝撃波角とマッハ数が正しく入力されているか確認して下さい")
                self.exceptflag = 1
        else:
            try:
                self.beta = float(settingwidget.betaedit.text()) / 180 * numpy.pi
                self.theta = float(settingwidget.thetaedit.text()) / 180 * numpy.pi
            except:
                QtGui.QMessageBox.warning(None,"Error",u"値の読込に失敗しました。\n衝撃波角と偏角が正しく入力されているか確認して下さい")
                self.exceptflag = 1

    def calculate(self):
        try:
            if self.want == 0:
                f = lambda beta : numpy.tan(self.theta) - ((self.mach ** 2.0 * numpy.sin(beta) ** 2.0 - 1.0) / numpy.tan(beta) / (1.0 + (1.0 / 2.0 * (self.kappa + 1.0) - numpy.sin(beta) ** 2.0) * self.mach ** 2))
                self.beta = opt.fsolve(f,0.00001,xtol=1e-5,maxfev = 1000)[0]

            elif self.want == 1:
                f = lambda theta : numpy.tan(theta) - ((self.mach ** 2.0 * numpy.sin(self.beta) ** 2.0 - 1.0) / numpy.tan(self.beta) / (1.0 + (1.0 / 2.0 * (self.kappa + 1.0) - numpy.sin(self.beta) ** 2.0) * self.mach ** 2))
                self.theta = opt.fsolve(f,0.00001,xtol=1e-5,maxfev = 1000)[0]

            else:
                f = lambda mach : numpy.tan(self.theta) - ((mach ** 2.0 * numpy.sin(self.beta) ** 2.0 - 1.0) / numpy.tan(self.beta) / (1.0 + (1.0 / 2.0 * (self.kappa + 1.0) - numpy.sin(self.beta) ** 2.0) * mach ** 2))
                self.mach = opt.fsolve(f,1.1,xtol=1e-5,maxfev = 1000)[0]
        except RuntimeWarning:
            QtGui.QMessageBox.warning(None,"Error",u"計算にに失敗しました。\n値が正しく入力されているか確認して下さい")





def main():
    def calculate():
        solve.readedit(settingwidget)
        if solve.exceptflag == 0:
            solve.calculate()
            settingwidget.betaedit.setText(str(round(solve.beta * 180 / numpy.pi,3)))
            settingwidget.thetaedit.setText(str(round(solve.theta * 180 / numpy.pi,3)))
            settingwidget.machedit.setText(str(round(solve.mach,3)))
            basex = [-10,10]
            basey = [0,0]
            thetax = [0,10]
            thetay = [0,10 * numpy.tan(solve.theta)]
            shockx = [0,10]
            shocky = [0,10 * numpy.tan(solve.beta)]
            dataplot.drawplot(basex,basey,thetax,thetay,shockx,shocky,hold = "false",legend = ["base-1","base-2","shock"],ylim = [-2,10])
        else:
            solve.exceptflag = 0


    qApp = QtGui.QApplication(sys.argv)
    mainwindow = QtGui.QMainWindow()
    mainwindow.setMinimumSize(400,400)
    mainwindow.setWindowTitle(u"θ-β-M関係式")
    mainpanel = QtGui.QWidget()

    settingwidget = SettingWidget(mainpanel)
    dataplot = Dataplot(mainpanel)
    solve = Solve()
    mainpanellayout = QtGui.QVBoxLayout()
    mainpanellayout.addWidget(settingwidget)
    mainpanellayout.addWidget(dataplot)
    mainpanel.setLayout(mainpanellayout)

    mainwindow.setCentralWidget(mainpanel)
    mainwindow.show()

    settingwidget.connect(settingwidget.exebutton,QtCore.SIGNAL('clicked()'),calculate)

    sys.exit(qApp.exec_())



if __name__ == '__main__':
    main()

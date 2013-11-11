# -*- coding: utf-8 -*-
# FILE: runXFOIL_alphaSweep.py

import subprocess
import shutil
import sys
import numpy

#----execute CFoil
ps = subprocess.Popen(['xfoil.exe'],
              stdin=subprocess.PIPE,
              stdout=None,
              stderr=None)

method = 1
pipe = bytes("plop\n g\n\n load {load} \noper\n visc {Re} \n pacc\n {filename} \n \n alfa{alpha}\n \n quit\n".format(load="dae31.dat",Re=450000,filename="a0_pwrt.dat",alpha=2),"ascii")
res = ps.communicate(pipe)

#----read XFoil Poler
fname = "a0_pwrt.dat"
lines = numpy.loadtxt(fname,skiprows=12)
if len(lines.shape)==2:
    lines = lines[-1,:]

print(lines)








#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      NaotoMORITA
#
# Created:     13/07/2014
# Copyright:   (c) NaotoMORITA 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import numpy, csv, binstr
import sys, os, random, copy,glob
#import to exe XFoil
import subprocess
import shutil
from matplotlib.pyplot import *

def normalize_foil(foilchord):
        foilchord = numpy.array(foilchord)
        x = foilchord[:,0]
        y = foilchord[:,1]
        fid2 = open("foil.foil",'w')
        fid2.write("foil\n")
        for i in range(numpy.shape(x)[0]):
            fid2.write(" {x_ele}  {y_ele} \n".format(x_ele = x[i], y_ele = y[i]))
        fid2.close()
        foil = "foil.foil"

        ps = subprocess.Popen(['xfoil'],stdin=subprocess.PIPE,stdout=None,stderr=None,shell=True)
        pipe = bytes("\nplop\n g\n\n norm\n load {load} \n pane\n GDES\n DERO\n eXec\n \n ppar \n n 300 \n \n \n save foil.foil\n y \n \n quit \n" .format(load=foil),"ascii")
        res = ps.communicate(pipe)

        foil = numpy.loadtxt("foil.foil",skiprows=1)

        #翼型座標の補間
        no = numpy.arange(0,101)
        x_out = numpy.array((no / 100) ** 1.75)
        #補間の種類
        sp_kind = "linear"
        #-----finding foil Leading Edge テスト
        i = int(0)
        while foil[i,0] > numpy.amin(foil[:,0]):
            i += 1
        LE = i + 1

        size = numpy.shape(foil[:,0])[0]+1
        buttomy = numpy.flipud(numpy.interp(x_out[:],numpy.flipud(foil[0:LE,0]),numpy.flipud(foil[0:LE,1])))
        uppery = numpy.interp(x_out[:],foil[LE-1:size,0],foil[LE-1:size,1])
        #self.x = numpy.append(numpy.flipud(self.x),numpy.delete(self.x,0))
        y_out = numpy.append(buttomy,numpy.delete(uppery,0))
        x_out = numpy.append(numpy.flipud(x_out),numpy.delete(x_out,0))
        foil_out = numpy.vstack([x_out,y_out]).T

        return foil_out,LE

def getfoilcordinate(filename):
    if not filename or not os.path.exists(filename):
        foilchord = numpy.array([[0.0,0.0],[0.0,0.0]])
    else:
        foilchord = numpy.loadtxt(filename,skiprows=1)
    return foilchord

def calc_camberandthickness(foil,LE):
    size = numpy.shape(foil)[0]
    camber = numpy.zeros([LE+1,1])
    thickness = numpy.zeros([LE+1,1])
    for i in range(LE+1):
        thickness[i] = foil[i,1] - foil[size-(1+i),1]
        camber[i] = (foil[i,1]+foil[size-(1+i),1])/2

    return camber,thickness

def curvature_energy(x,y):
    #曲率と歪みエネルギーの演算
    #二次精度中心差分
    size = numpy.shape(x)[0]
    dx = numpy.zeros(size)
    dy = numpy.zeros(size)
    ddx = numpy.zeros(size)
    ddy = numpy.zeros(size)
    for i in range(0,size-1):
        dx[i] = x[i+1]-x[i]
        dy[i] = y[i+1]-y[i]
    dx[size-1] = dx[size-2]
    dy[size-1] = dy[size-2]

    for i in range(0,size-1):
        ddx[i] = dx[i+1]-dx[i]
        ddy[i] = dy[i+1]-dy[i]
    ddx[size-1] = ddx[size-2]
    ddy[size-1] = ddy[size-2]

    E = 0
    curvature = numpy.zeros(size)
    dE = numpy.zeros(size)
    for i in range(size-1):
        curvature[i] = (ddx[i]*dy[i]-ddy[i]*dx[i])/((dx[i]**2+dy[i]**2)**(3/2))
        dE[i] =(ddx[i]*dy[i]-ddy[i]*dx[i])**2/((dx[i]**2+dy[i]**2)**(5/2)) * abs(x[i+1]-x[i])
        E += dE[i]
    return E,curvature

#ARFFデータを作る dataset:データファイル名　writedata:書き込むデータ　[E , camberE , thicknessE , LE_curvature , TEangle,PR]
def make_ARFF(dataset,writedata):
    if not dataset or not os.path.exists(dataset):
        f = open(dataset,'w')
        f.write("@relation foildataset\n")
        f.write("@attribute Chord_Strain_E numeric\n")
        f.write("@attribute Camber_Strain_E numeric\n")
        f.write("@attribute Thickeness_Strain_E numeric\n")
        f.write("@attribute LE_curvature numeric\n")
        f.write("@attribute TE_angle numeric\n")
        f.write("@attribute max_camber numeric\n")
        f.write("@attribute pos_max_camber numeric\n")
        f.write("@attribute max_thickness numeric\n")
        f.write("@attribute pos_max_thickness numeric\n")

        f.write("@attribute propriety {true,false}\n")
        f.write("@data\n")
        f.write("{E},{CE},{ThE},{LEC},{TEA},{Cmax},{Cmax_pos},{Thmax},{Thmax_pos},{PR}\n".format(E = writedata[0],CE = writedata[1],ThE = writedata[2],LEC = writedata[3],TEA = writedata[4],Cmax =writedata[5],Cmax_pos = writedata[6],Thmax = writedata[7], Thmax_pos = writedata[8],PR = writedata[9]))
        f.close()
    else:
        f = open(dataset,'a')
        f.write("{E},{CE},{ThE},{LEC},{TEA},{Cmax},{Cmax_pos},{Thmax},{Thmax_pos},{PR}\n".format(E = writedata[0],CE = writedata[1],ThE = writedata[2],LEC = writedata[3],TEA = writedata[4],Cmax =writedata[5],Cmax_pos = writedata[6],Thmax = writedata[7], Thmax_pos = writedata[8],PR = writedata[9]))
        f.close()
#キャンバ試してみると良いかも

def read_ARFF(dataset):
    dataTF = numpy.genfromtxt(dataset,dtype='str',skiprows=12,delimiter = ',')
    try:
        numpy.shape(dataTF)[1]
        size = numpy.shape(dataTF)[0]
    except:
        size = 1
    jT = []
    jF = []
    for i in range(size):
        if dataTF[i][9] =='true':
            jT.append(i)
        else:
            jF.append(i)
    dataTF = numpy.loadtxt(dataset,skiprows=12,delimiter = ',',usecols = (0,1,2,3,4,5,6,7,8))
    dataF = []
    dataT = []
    for j in jT:
        dataT.append(dataTF[j])
    for j in jF:
        dataF.append(dataTF[j])
    dataT = numpy.array(dataT)
    dataF = numpy.array(dataF)
    return dataT,dataF

def mahalanobis(Y,data):
    cov_data = numpy.cov(data.T,bias = 0)

    ave_data = numpy.array([numpy.mean(data,axis = 0)])
    y = numpy.array([Y])
    covinv = numpy.linalg.inv(cov_data)
    dist = y-ave_data
    calcbuff = numpy.dot(dist,covinv)
    m_dist = numpy.dot(calcbuff,dist.T)**(0.5)
    print(m_dist[0][0])


def main():
    pwd = os.getcwd()
    os.chdir("C:/Users/NaotoMORITA/Desktop/航空/翼型")

    #foilname = input('input foilname > ')
    flist = glob.glob("C:/Users/NaotoMORITA/Desktop/航空/翼型/*.*")
    for foilname in flist:
        foilchord = getfoilcordinate(foilname)
        os.chdir(pwd)
        buff = normalize_foil(foilchord)
        norm_chord = buff[0]
        buff1 = calc_camberandthickness(norm_chord,100)
        camber = buff1[0]
        thickness = buff1[1]
        chord_outbuff = curvature_energy(norm_chord[:,0],norm_chord[:,1])
        chord_E = chord_outbuff[0]
        chord_LEC = (abs(chord_outbuff[1][100])+abs(chord_outbuff[1][100])+abs(chord_outbuff[1][100]))/3

        camber_outbuff = curvature_energy(norm_chord[0:101,0],camber[:])
        camber_E = camber_outbuff[0]

        thickness_outbuff = curvature_energy(norm_chord[0:101,0],thickness[:])
        thickness_E = thickness_outbuff[0]

        #後縁角
        TE_dot = (norm_chord[199,0]-norm_chord[200,0])*(norm_chord[1,0]-norm_chord[0,0])+(norm_chord[199,1]-norm_chord[200,1])*(norm_chord[1,1]-norm_chord[0,1])
        a_abs = numpy.sqrt((norm_chord[199,0]-norm_chord[200,0])**2+(norm_chord[199,1]-norm_chord[200,1])**2)
        b_abs = numpy.sqrt((norm_chord[1,0]-norm_chord[0,0])**2+(norm_chord[1,1]-norm_chord[0,1])**2)
        TEangle = numpy.arccos(TE_dot/a_abs/b_abs)*180/numpy.pi

        #最大キャンバとその位置
        Cmax = numpy.amax(abs(camber[:]))
        Cmax_pos = norm_chord[numpy.argmax(abs(camber[:])),0]
        #最大キャンバとその位置
        Thmax = numpy.amax(abs(thickness[:]))
        Thmax_pos = norm_chord[numpy.argmax(abs(thickness[:])),0]

        plot(norm_chord[:,0],norm_chord[:,1])
        hold(True)
        plot(norm_chord[0:101,0],camber[:])
        axis('equal')
        show()
        TF = input('good:g bad:b non:n > ')
        print(TF)
        if TF == 'g':
            print('good')
            writedata = [chord_E,camber_E,thickness_E,chord_LEC,TEangle,Cmax,Cmax_pos,Thmax,Thmax_pos,'true']
            make_ARFF('foildataset.arff',writedata)
        elif TF == 'b':
            print('bad')
            writedata = [chord_E,camber_E,thickness_E,chord_LEC,TEangle,Cmax,Cmax_pos,Thmax,Thmax_pos,'false']
            make_ARFF('foildataset.arff',writedata)

        dataTF_buff = read_ARFF('foildataset.arff')
        dataT = dataTF_buff[0]
        dataF = dataTF_buff[1]

        if numpy.shape(dataT)[0] > 1 and numpy.shape(dataF)[0] > 1 :
            mahalanobis([chord_E,camber_E,thickness_E,chord_LEC,TEangle,Cmax,Cmax_pos,Thmax,Thmax_pos],dataT)
            mahalanobis([chord_E,camber_E,thickness_E,chord_LEC,TEangle,Cmax,Cmax_pos,Thmax,Thmax_pos],dataF)

if __name__ == '__main__':
    main()

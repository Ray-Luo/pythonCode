import auxil.auxil as auxil
import numpy as np 
from osgeo import gdal   
from osgeo.gdalconst import GA_ReadOnly,GDT_Float32
import matplotlib.pyplot as plt
from pylab import *
import gc

def Indices(in_path,M, Count):  

#   Input NDVI file
    print "***************"
    print str(M)
    gdal.AllRegister()
    band_NDVI = gdal.Open(in_path+"/MOD13A2.MRTWEB.A"+M+".005.1_km_16_days_NDVI_cut.tif",GA_ReadOnly)
    try:
        cols1 = band_NDVI.RasterXSize
        rows1 = band_NDVI.RasterYSize
        bands1 = band_NDVI.RasterCount
    except StandardError, e:
        print "Error: "+str(M)+"_NDVI is missing"
        exit(1)
    

#   Input LST file
    if(1):
        band_LST = gdal.Open(in_path+"/MOD11A2.MRTWEB.A"+M+".005.LST_Day_1km_cut.tif",GA_ReadOnly)
#    print (band_LST is None)   
    if(band_LST is None): 
        band_LST = gdal.Open(in_path+"/MOD11A2.MRTWEB.A"+M+".041.LST_Day_1km_cut.tif",GA_ReadOnly)
    if(band_LST is None):
        band_LST = gdal.Open(in_path+"/MOD11A2.MRTWEB.A"+M+".004.LST_Day_1km_cut.tif",GA_ReadOnly)
    if(band_LST is None):
        band_LST = gdal.Open(in_path+"/MOD11A2.MRTWEB.A"+M+".005.LST_Day_1km_cut.tiff",GA_ReadOnly)
    if(band_LST is None):
        band_LST = gdal.Open(in_path+"/MOD11A2.MRTWEB.A"+M+".041.LST_Day_1km_cut.tiff",GA_ReadOnly)
    if(band_LST is None):
        band_LST = gdal.Open(in_path+"/MOD11A2.MRTWEB.A"+M+".004.LST_Day_1km_cut.tiff",GA_ReadOnly)
    try:
        cols2 = band_LST.RasterXSize
        rows2 = band_LST.RasterYSize
        bands2 = band_LST.RasterCount
    except StandardError, e:
        print "Error: "+str(M)+"_LST is missing"
        exit(1)

#   Check if LST and NDVI have the same size
    if (cols1 != cols2) or (rows1 != rows2) or (bands1 != bands2):
        print "Error: "+M+"_NDVI and "+M+"_LST have different size. Please correct the error, delete all the output files and run the program again!"
        exit(1)
        
#   Check if LST and NDVI have spatial reference       
    projInfo1 = band_NDVI.GetProjection()
    transInfo1 = band_NDVI.GetGeoTransform()
    projInfo2 = band_LST.GetProjection()
    transInfo2 = band_LST.GetGeoTransform()

    if((str(projInfo1)=="") or (str(projInfo2)=="") or (str(transInfo1)=="") or (str(transInfo2)=="")):
        print "Error: "+str(M)+" images do not spatial reference."
        exit(1)
    
    if((projInfo1 !=projInfo2)):
        print "Error: "+str(M)+" images have different pro spatial reference."
        exit(1)

#   Make Matrix
    NDVI=(band_NDVI.ReadAsArray().astype(float))*0.0001
    NDVI[NDVI==np.amin(NDVI)] = np.nan
    LST=(band_LST.ReadAsArray().astype(float))*0.02-273.15
    LST[LST==np.amin(LST)] = np.nan

# Getting rid of the Nan    
    i = 0
    j = 0
    v = np.ones((rows1,cols1),dtype=list)
    while i < rows1:
        while j < cols1:
            v[i,j] = (NDVI[i,j],LST[i,j])
            j = j + 1
        i = i + 1
        j = 0
    #print v[1000,1000]
    v.shape=(1, rows1*cols1)
    v=list(v)      
    print type(v)
    print "1111111"
    w=[]
    i=0
    while i < rows1*cols1:
        w.append(v[0][i])
        i=i+1
    print w[0][1]
    good = []
    for i in w:
        if ((not(np.isnan(i[0]))) and (not(np.isnan(i[1])))):
            good.append(i)

    for i in good:
        if (np.isnan(i[0])):
            print "What!"


    
#   Sort the matrix using LST and NDVI value
    sort_lst = sorted(good, key=lambda v_tuple:v_tuple[1])
    sort_ndvi = sorted(good, key=lambda v_tuple:v_tuple[0])
    print sort_lst[-1]
    print len(sort_lst)
    print np.amax(sort_lst)



#   Find the NDVI value which has the highest LST
#   In every 0.01 NDVI interval, choose 10 highest LST points and calculate the mean value
#   Compare each highest LST and find the biggest value and its corresponding NDVI value


#   Calculate the Dry Edge
#   In every 0.01 NDVI interval, find the highest 5 LST points. Recode them and their corresponding NDVI value



#   Calculate Wet Edge
#   In every 0.01 NDVI interval, find the lowest 10 LST points. Recode them and calculate their mean value



#   Ready to draw the dry edge and wet edge



    y=[]
    x1=range(0,100)
    x=[]
    y2=[]

    plt.plot(NDVI,LST,"r*")
    plt.axis([0,1,0,20])
    plt.xlabel("NDVI")
    plt.ylabel("Temperature/c")
    plt.show()
    




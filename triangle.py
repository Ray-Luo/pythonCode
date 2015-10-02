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
    T_temp = []
    T_start = []
    i = 0
    j = 0
    temp1 = 0
    temp2 = 0
    k = 0
    m = 0
    ndvi_start = 0
    print sort_ndvi[-1][0]
    while i<sort_ndvi[-1][0]:   
        while j < len(sort_ndvi):
            if i<sort_ndvi[j][0]<i+0.01:
                T_start.append(sort_ndvi[j])
            j = j + 1
        T_start = sorted(T_start, key=lambda v_tuple:v_tuple[1])
        if (len(T_start))>5:
            T_start = T_start[-5:]
        else:
            T_start = T_start[:]
        
        
        if (len(T_start)!=0):
            for p in T_start:
                T_temp.append(p)
            for o in T_temp:
                k = k + o[1]
                m = m + o[0]
               # print m, o[0]
            k = k / len(T_temp)
            m = m / len(T_temp)
            if temp1 >= k:
                temp1 = temp1
                temp2 = temp2
            else:
                temp1 = k
                temp2 = m
        print temp1, temp2 , len(T_temp)
        j = 0
        T_start = []
        T_temp = []
        i = i + 0.01
        k = 0
        m = 0
    ndvi_start = temp2
    print temp1
    print temp2

#   Calculate the Dry Edge
#   In every 0.01 NDVI interval, find the highest 5 LST points. Recode them and their corresponding NDVI value
    i = ndvi_start
    j = 0
    c=[]
    z_max=[]
    z_max_temp =[]
    if (i >= sort_ndvi[-1][0]):
        return "Please check the data, something might be wrong."
    if (i<sort_ndvi[-1][0]):
        while i<sort_ndvi[-1][0]: 
            while j < len(sort_lst):
                if i<sort_ndvi[j][0]<i+0.01:
                    c.append(sort_ndvi[j])
                j=j+1

            if len(c)==0:
                print "c = 0"     
            c=sorted(c, key=lambda v_tuple:v_tuple[1])        
            print len(c)
            if len(c)>5:
                z_max_temp = c[-5:]
            if len(c)<=5:
                z_max_temp = c[:]
                
            print len(z_max_temp)
            print "############################"

            for j in z_max_temp:
                z_max.append(j)
            
            j=0
            c=[]
            z_max_temp =[]
            i=i+0.01
            print i
        z_max=sorted(z_max, key=lambda v_tuple:v_tuple[0])
        print len(z_max)
        



#   Calculate Wet Edge
#   In every 0.01 NDVI interval, find the lowest 10 LST points. Recode them and calculate their mean value
    i = 0
    j = 0
    z_min = []
    z_min_temp = []
    while i<sort_ndvi[-1][0]:   
        while j < len(sort_ndvi):
            if i<sort_ndvi[j][0]<i+0.01:
                z_min_temp.append(sort_ndvi[j])
            j = j + 1
        z_min_temp = sorted(z_min_temp, key=lambda v_tuple:v_tuple[1])
        if(len(z_min_temp)>5):
            z_min_temp = z_min_temp[0:5]
        else:
            z_min_temp = z_min_temp[0:5]
        for p in z_min_temp:
            z_min.append(p)
        j = 0
        z_min_temp = []
        i = i + 0.01

    print z_min[0]            
    k = 0
    for i in z_min:
        k = k + i[1]
    LST_min=k/len(z_min)
    print "*************"
    print LST_min


#   Ready to draw the dry edge and wet edge
    m=[]
    n=[]
    for s in z_max:
        m.append(s[0])
        n.append(s[1])

#   regression
    p = np.polyfit(m,n,1)
    print p
    p=list(p)
    print p[0],p[1]
    slope=p[0]
    intercp=p[1]
    y=[]
    x1=range(0,100)
    x=[]
    y2=[]
    for i in x1:
        y1=float(i)*slope/100+intercp
        y.append(y1)
        x.append(float(i)/100)
        y2.append(LST_min)
    plt.plot(x,y,"r-",NDVI,LST,"r*",m,n,"b*",x,y2,"r-")
    plt.axis([0,1.2,0,70])
    plt.xlabel("NDVI")
    plt.ylabel("Temperature/c")
    plt.text(0.2,60,'LST ='+str(slope)+'*NDVI'+'+'+str(intercp))
    plt.text(0.2,63,"Date: "+M)
    plt.text(0.2,57,"Wet Edgy = "+ str(LST_min))
    savefig(str(M)+'.png')
    plt.close()
    



#   write regression equation to txt
    M = str(M)
    f = open("output.txt","a")
    print >>f , "\n"+"Dry Edge Equation"
    if Count > 0:
        f.write(M+": LST="+ str(slope) + "*NDVI+" + str(intercp)+"\n")
        Count = Count - 1
    if Count == 0:
        f.close()
        
    
#   calculate TVDI
    TVDI=(LST-LST_min)/(intercp+slope*NDVI-LST_min)
    TVDI[TVDI<0]=0
    TVDI[TVDI>1]=1


#   write TVDI to disk
    M = str(M)
    driver = gdal.GetDriverByName("GTiff")
    outDataset = driver.Create(M+"_cut_TVDI.tif",
                        cols1,rows1,bands1,GDT_Float32)
    projInfo = band_NDVI.GetProjection()
    transInfo = band_NDVI.GetGeoTransform()
    outDataset.SetProjection(projInfo)
    outDataset.SetGeoTransform(transInfo)
    TVDI_band = outDataset.GetRasterBand(1)
    TVDI_band.WriteArray(TVDI[:,:])
    TVDI_band.FlushCache()
    TVDI_band = None
    outDataset = None


#   calculate RSM
    RSM_D = 107.75+1.71*slope
    RSM = 100 - TVDI*(100-RSM_D)
    RSM[RSM>100]=100


#   write RSM to disk
    driver = gdal.GetDriverByName("GTiff")
    outDataset = driver.Create(M+"_cut_RSM.tif",
                        cols1,rows1,bands1,GDT_Float32)
    projInfo = band_NDVI.GetProjection()
    transInfo = band_NDVI.GetGeoTransform()
    outDataset.SetProjection(projInfo)
    outDataset.SetGeoTransform(transInfo)
    RSM_band = outDataset.GetRasterBand(1)
    RSM_band.WriteArray(RSM[:,:])
    RSM_band.FlushCache()
    RSM_band = None
    outDataset = None

#   delete variables and release memory
    del band_NDVI, cols1,rows1,bands1, band_LST, cols2, rows2,bands2
    del projInfo1,transInfo1,projInfo2,transInfo2
    del good,NDVI,LST
    del v,w,f,Count
    del sort_lst,sort_ndvi
    del T_temp,T_start
    del c,z_max,z_max_temp
    del z_min,z_min_temp
    del m,n
    del p,y,x1,x,y2,slope,intercp
    del TVDI,driver,outDataset,projInfo,transInfo,TVDI_band,RSM_D,RSM,RSM_band
    gc.collect()
                

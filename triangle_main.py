import os
from triangle import Indices
import auxil.auxil as auxil
import gc


def main():

#   input directory    
    in_path = auxil.select_directory(title="Choosing the input file directory")

#   imagery dataset
    lista = os.listdir(in_path)
    print in_path
    GQ = []
    data_list=[]
    i = 0
    for k in range(len(lista)):
        GQ.append(str(lista[k]))
#

    for k in GQ:
        try:
            if float(k[16:23]) > 0 :
                data_list.append(k[16:23])
        except StandardError, e:
            print ""

    print data_list[0:len(data_list)/2]
#   Output txt
    Count = len(data_list)/2
    for m in data_list[0:len(data_list)/2]:
        print m
        print type(m)
        Indices(in_path, m, Count)
    print m
        




if __name__ == '__main__':
    main()

"""
print GQ[0], GQ[1]
    print GQ[0][-8:]
    GQ[0] = GQ[0][::-1]
    t = GQ[0].index("_")
    print t
    print len(GQ[0])
    print GQ[0][t:]


"""

import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image

with open('id.txt') as id:
 contents= id.read()
 lines = contents.split('\n')


for line in lines:
 filename = str(line)+"_V1.nii.gz"
 v1 = nib.load(filename)
 data = v1.get_fdata()
 shape = data.shape
 vectorname = str(line)+".txt"
 f = open(vectorname, "w")
 for i, x in enumerate(data):
  for j, y in enumerate(x):
   for k, z in enumerate(y):
    i=i
    j=j
    k=k
    a=int(round(np.abs(z[0]) * 255))
    b=int(round(np.abs(z[1]) * 255))
    c=int(round(np.abs(z[2]) * 255))
    f.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(i,j,k,a,b,c))

for line in lines:
 vectorname = str(line)+".txt"
 vector = np.loadtxt(vectorname)
 dict = {}
 for row in vector:
   value = int(row[2])
   if value not in dict:
     dict[value] = []
   dict[value].append(row)
 for key, value in dict.items():
   array = np.array(value)
   np.savetxt(str(line)+"_"+str(key) + ".txt", np.delete(array, 2, axis=1))
   data = np.loadtxt(str(line)+"_"+str(key) + ".txt")
   rows= int(data[:,0].max()) + 1
   cols= int(data[:,1].max()) + 1
   image = np.zeros((rows, cols, 3))
   for row in data:
    i = int(row[0])
    j = int(row[1])
    r = row[2] / 255
    g = row[3] / 255
    b = row[4] / 255
    image[i,j,:] = [r,g,b]
   image = np.rot90(image, k=1)
   plt.imshow(image)
   plt.imsave(str(line)+"_"+str(key)+".png", image)
















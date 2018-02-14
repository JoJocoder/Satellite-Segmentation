import cv2
import numpy as np
import os
OTHER=0
VEGETATION=1
BUILDING=3
WATER=4
ROAD=2
VColor=[159,255,84]
RColor=[38,71,139]
BColor=[34,180,238]
WColor=[255,191,0]
def set_labels(inputpath,outpath):
	url=[]
	for pic in os.listdir(inputpath):
		url.append(pic)
		src=cv2.imread(inputpath+'/'+pic,0)
		rows,cols=src.shape
		for i in range(rows):
			for j in range(cols):
				p_mask=src.item(i,j)
				if p_mask==ROAD:
					src.itemset((i,j),1)
				else:
					src.itemset((i,j),0)
		cv2.imwrite(outpath+'/'+pic,src)
if __name__ == '__main__':
	set_labels(r'G:\Datas\BDCI2017-jiage\CCF-training\unet_train\road\labels',r'G:\Datas\BDCI2017-jiage\CCF-training\unet_train\road\roads')

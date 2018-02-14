import cv2
import numpy as np

OTHER=0
VEGETATION=1
BUILDING=3
WATER=4
ROAD=2
VColor=[159,255,84]
RColor=[38,71,139]
BColor=[34,180,238]
WColor=[255,191,0]
def draw_labels(argc,argv):
	input_src=argv[1]
	input_mask=argv[0]
	mask=cv2.imread(input_mask,0)
	src=cv2.imread(input_src)
	rows,cols,all=src.shape
	for i in range(rows):
			for j in range(cols):
				p_mask=mask.item(i,j)
				if p_mask==VEGETATION:
					src.itemset((i,j,0),VColor[0])
					src.itemset((i,j,1),VColor[1])
					src.itemset((i,j,2),VColor[2])
				elif p_mask==ROAD:
					src.itemset((i,j,0),RColor[0])
					src.itemset((i,j,1),RColor[1])
					src.itemset((i,j,2),RColor[2])
				elif p_mask==BUILDING or p_mask==255:
					src.itemset((i,j,0),BColor[0])
					src.itemset((i,j,1),BColor[1])
					src.itemset((i,j,2),BColor[2])
				elif p_mask==WATER:
					src.itemset((i,j,0),WColor[0])
					src.itemset((i,j,1),WColor[1])
					src.itemset((i,j,2),WColor[2])
	cv2.imwrite(argc,src)
if __name__ == '__main__':
	draw_labels('G:/Datas/train1show.png',['G:/Datas/BDCI2017-jiage-Semi/training/train1_labels_8bits.png','G:/Datas/BDCI2017-jiage-Semi/training/train1.png'])
	

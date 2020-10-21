import numpy as np
from PIL import ImageGrab
import cv2

bound = [] #x,y,x1,y1

def grab():
	image = ImageGrab.grab(bbox =(0,50, 1280, 740) ,all_screens=True)

	return np.array(image)
	#if a>12:
	#	return a

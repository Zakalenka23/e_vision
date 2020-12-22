import numpy as np
from PIL import ImageGrab
import cv2

bound = [] #x,y,x1,y1

def grab():
	image = ImageGrab.grab(bbox =(320,180,1600,900) ,all_screens=True)

	return np.array(image)
import cv2
import matplotlib.pyplot as plt
import numpy as np
import grabber as grab
import time
import math
import joystick
#"C:/car vision proj/media/scr.jpg"
#path = "C:/car vision proj/media/DR101423.AVI"
#path = "D:/Denis/Downloads/2020-12-12 23-32-11.mp4"
#path = "C:/car vision proj/media/withoutsound.mp4"
#path = "D:/Denis/Downloads/withoutsound.mp4"
path = "D:/video/2020-12-12 23-32-11.mp4"
class visor():
    def __init__(self, colorimage):
        if type(colorimage) == type("sample"):
            self.colorimage = cv2.imread(colorimage)
            
        else:
            self.colorimage = colorimage
        
        

        self.image = cv2.cvtColor(self.colorimage, cv2.COLOR_BGR2GRAY)
        #self.image = np.multiply(self.image, 10)


        self.lineColor = ((0,255,0),(0,0,255),(78,237,232)) # blue green red
        self.line_thickness = 2 
        self.canny_treshold = (50, 250)
        self.polygons = [[(80, 719), (1200,719),(727+40,320), (610-40,320)]] #MAUN ###############################
        #self.polygons = [[(0, 719), (1280,719),(640,360)]] #triangle
        #self.polygons = [[(0, 719), (1280,719),(640,360)]]
        #image parameters
        self.imageHeight = self.image.shape[0] #720 
        self.imageWidth = self.image.shape[1] #1280 

        self.lines = None
        self.leftLine = None
        self.rightLine = None
        self.averegedLines = None

        #images
        self.canny_image = None
        self.cropped_image = None
        self.line_image = None


        # Hough parameters
        self.RHO = 1 
        self.theta = np.pi/360
        self.houhgVoteTreshold = 50
        self.minLineLength = 20
        self.maxLineGap = 20


        self.slopeTreshold = 1 #0.5


        self.parCounter = 0

        self.foo = 0
        self.verticalLine = np.array([640, self.imageHeight, 640, 0])
        self.DoDisplayVerticalLine = True
    
        self.leftLineOLD = None
        self.rightLineOLD = None


    def canny(self):
        kernel = np.ones((7,7),np.float32)/40
        blur = cv2.filter2D(self.image,-1,kernel)
        #blur = cv2.GaussianBlur(self.image ,(7,7),0)
        self.canny_image = cv2.Canny(blur, self.canny_treshold[0], self.canny_treshold[1])


    def cropImage(self):
        polygon = np.array(self.polygons)
        mask = np.zeros_like(self.image)
        cv2.fillPoly(mask, polygon, 255)
        self.cropped_image = cv2.bitwise_and(self.canny_image, mask)


    def makeLines(self):
        self.lines = cv2.HoughLinesP(self.cropped_image,self.RHO,self.theta, self.houhgVoteTreshold, minLineLength = self.minLineLength, maxLineGap = self.maxLineGap)
    #@staticmethod
    def makeCoordinates(self, lineParameters):
        slope, intercept = lineParameters
        y1 = self.imageHeight
        y2 = int(y1*(3/5))
        x1 = int((y1 - intercept)/slope) 
        x2 = int((y2 - intercept)/slope) 
        return np.array([x1,y1, x2,y2, 0])


    def averageLines(self):
        leftFit = []
        rightFit = []
        if self.lines is not None:
            for line in self.lines:
                x1, y1, x2, y2 = line.reshape(4)
                slope, intercept = np.polyfit((x1,x2), (y1,y2), 1)
                if slope < -self.slopeTreshold: #исх <
                    leftFit.append((slope, intercept))
                    #leftSlope.append(slope)
                elif slope > self.slopeTreshold: #>
                    rightFit.append((slope, intercept))
                    #rightSlope.append(slope)
            self.leftFitAVG = np.average(leftFit, axis=0)
            self.rightFitAVG = np.average(rightFit, axis=0)

            try:
                self.leftLine = self.makeCoordinates(self.leftFitAVG)               
            except Exception as e:
                # print(e, '\n')
                # self.leftLine = np.array([0,0,0,0])             
                pass
            try:
                self.rightLine = self.makeCoordinates(self.rightFitAVG)
            except Exception as e:
                pass
                #print(e, '\n')
                #self.rightLine = np.array([0,0,0,0])




            #debug
            if self.DoDisplayVerticalLine == True:
                self.averegedLines = np.array([self.leftLine,self.rightLine, self.verticalLine])
            else:
                self.averegedLines = np.array([self.leftLine,self.rightLine])#, self.verticalLine])


    def newDisplayer(self): #lines = self. ...
        self.line_image = np.copy(self.colorimage)
        if self.leftLine is not None:
            lx1, ly1, lx2, ly2, lcolor = self.leftLine.reshape(5)
            cv2.line(self.line_image, (lx1,ly1), (lx2,ly2), self.lineColor[lcolor], self.line_thickness)
            self.leftLine = np.array([lx1, ly1, lx2, ly2, 1])
            self.leftLineOLD = np.copy(self.leftLine)
        if self.rightLine is not None:
            rx1, ry1, rx2, ry2, rcolor = self.rightLine.reshape(5)
            cv2.line(self.line_image, (rx1,ry1), (rx2,ry2), self.lineColor[rcolor], self.line_thickness)
            self.rightLine = np.array([rx1, ry1, rx2, ry2, 1])
            self.rightLineOLD = np.copy(self.rightLine)


    

    def updateImage(self, colorimage):
        self.colorimage = colorimage
        self.image = cv2.cvtColor(self.colorimage, cv2.COLOR_BGR2GRAY)
        
        self.image = self.image + 45
        #self.image *= 2
        self.imageHeight = self.image.shape[0] #720 
        self.imageWidth = self.image.shape[1] #1280 

    def show(self):
        cv2.cv2.imshow("lines", self.line_image) #self.line_image)
        cv2.imshow("cropImage", self.cropped_image)
        #cv2.imshow("cropImage", self.canny_image)



    def lineCorrection(self):
        if self.leftLine is not None or self.rightLine is not None:
            try:
                if (self.leftLine[4] == 0) and (self.rightLine[4] !=0):
                    dx1, dy1, dx2, dy2 = 0,0,0,0
                    dx1 = self.leftLine[0] - self.leftLineOLD[0]
                    dy1 = self.leftLine[1] - self.leftLineOLD[1]
                    dx2 = self.leftLine[2] - self.leftLineOLD[2] 
                    dy2 = self.leftLine[3] - self.leftLineOLD[3]
                    a = [self.rightLine[0]+dx1, self.rightLine[1]+dy1, self.rightLine[2]+dx2, self.rightLine[3]+dy2, 2]
                    self.rightLine = np.array(a)


                if (self.rightLine[4] == 0) and (self.leftLine[4] !=0):
                    dx1, dy1, dx2, dy2 = 0,0,0,0
                    dx1 = self.rightLine[0] - self.rightLineOLD[0]
                    dy1 = self.rightLine[1] - self.rightLineOLD[1]
                    dx2 = self.rightLine[2] - self.rightLineOLD[2] 
                    dy2 = self.rightLine[3] - self.rightLineOLD[3]
                    a = [self.leftLine[0]+dx1, self.leftLine[1]+dy1, self.leftLine[2]+dx2, self.leftLine[3]+dy2, 2]
                    self.leftLine = np.array(a)
            except Exception as e:
                #print(e)
                pass

    def Do(self):
        self.canny()
        self.cropImage()
        self.makeLines()
        self.newDisplayer()
        self.averageLines()
        self.lineCorrection()



    def debug(self):
        try:
            #эта хуйня кароче вычисляет постоянный наклон (поворот дороги )
            leftVector = np.array([self.leftLine[0] - self.leftLine[2], self.leftLine[1] - self.leftLine[3]])
            rightVector = np.array([self.rightLine[0] - self.rightLine[2], self.rightLine[1] - self.rightLine[3]])
            #print(leftVector, rightVector)
            #print(leftVector + rightVector, "\n")
            diff = (1280/2) -  np.average([self.leftLine[0],   self.rightLine[0]])
            force = diff #((diff/10))**2
            # if diff<0:
            #     force = -force 
            return force*1.5
        except Exception as e:
            return 0



foo = True
# #video 
cap = cv2.VideoCapture(path)
_, startImage = cap.read()
visor = visor(colorimage = startImage)
while (cap.isOpened()) and foo:
    _, image = cap.read()
    visor.updateImage(image)
    visor.Do()
    visor.show()
    #force = visor.debug()
    #joystick.setMouseByForce(force)
    if cv2.waitKey(16) == ord(' '):
         break

#############################################screen capture
# startImage = grab.grab()
# visor = visor(colorimage = startImage)

# while True:
#     image = grab.grab()
#     visor.updateImage(image)
#     visor.Do()
#     visor.show()
#     force = visor.debug()
#     joystick.setMouseByForce(force)
#     if cv2.waitKey(33) == ord(' '):
#         break


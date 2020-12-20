import cv2
import matplotlib.pyplot as plt
import numpy as np
import imageGrabber as grab
import time
import math
#"C:/car vision proj/media/scr.jpg"
#path = "C:/car vision proj/media/DR101423.AVI"
#path = "D:/video/2020-12-12 23-32-11.mp4"
path = "C:/car vision proj/media/withoutsound.mp4"

class visor():
    def __init__(self, colorimage):
        if type(colorimage) == type("sample"):
            self.colorimage = cv2.imread(colorimage)
            
        else:
            self.colorimage = colorimage
        
        

        self.image = cv2.cvtColor(self.colorimage, cv2.COLOR_BGR2GRAY)
        self.image = np.multiply(self.image, 10)


        self.lineColor = ((0,255,0),(0,0,255),(78,237,232)) # blue green red
        self.line_thickness = 2 
        self.canny_treshold = (50, 150)
        #self.polygons = [[(0, 719), (1280,719),(970,550), (420,550)]]
        #self.polygons = [[(200,720),(1100,720),(800,540),(580,540)]]#ETS STANDART BUMPER
        #self.polygons = polygons = [[(0, 719), (1280,719),(1280,0), (0,0)]] #full
        self.polygons = [[(0, 719), (1280,719),(640,360)]] #triangle
        #self.polygonsTEST = [[(0, 719), (1280,719),(640,360)]]
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
        self.maxLineGap = 30


        self.slopeTreshold = 0.5


        self.parCounter = 0

        self.foo = 0
        self.verticalLine = np.array([640, self.imageHeight, 640, 0])
        self.DoDisplayVerticalLine = True
    
        self.leftLineOLD = None
        self.rightLineOLD = None


    def canny(self):
        blur = cv2.GaussianBlur(self.image ,(7,7),0)
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
                if slope < -self.slopeTreshold:
                    leftFit.append((slope, intercept))
                    #leftSlope.append(slope)
                elif slope > self.slopeTreshold:
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
        if self.leftLine is not None and self.rightLine is not None:
            lx1, ly1, lx2, ly2, lcolor = self.leftLine.reshape(5)
            rx1, ry1, rx2, ry2, rcolor = self.rightLine.reshape(5)
            cv2.line(self.line_image, (lx1,ly1), (lx2,ly2), self.lineColor[lcolor], self.line_thickness)
            cv2.line(self.line_image, (rx1,ry1), (rx2,ry2), self.lineColor[rcolor], self.line_thickness)
            self.leftLine = np.array([lx1, ly1, lx2, ly2, 1])
            self.leftLineOLD = np.copy(self.leftLine)
            self.rightLine = np.array([rx1, ry1, rx2, ry2, 1])
            self.rightLineOLD = np.copy(self.rightLine)


    def displayLines(self): #image, lines, line_thickness, lineColor):
        self.line_image = np.copy(self.colorimage)
        if self.averegedLines is not None:
            for line in self.averegedLines: #self.averegedLines:
                x1, y1, x2,y2 = line.reshape(4)
                try:
                    cv2.line(self.line_image, (x1,y1), (x2,y2), self.lineColor, self.line_thickness)
                except Exception as e:
                    pass
                    #print(e, "\n")

    def debugLine(self): #image, lines, line_thickness, lineColor):
        self.line_image = np.copy(self.colorimage)
        if self.verticalLine is not None:
            x1, y1, x2,y2 = self.verticalLine.reshape(4)
            try:
                cv2.line(self.line_image, (x1,y1), (x2,y2), self.lineColor, self.line_thickness)
            except Exception as e:
                pass
                #print(e, "\n")

    def updateImage(self, colorimage):
        self.colorimage = colorimage
        self.image = cv2.cvtColor(self.colorimage, cv2.COLOR_BGR2GRAY)
        self.image = self.image - 40
        self.imageHeight = self.image.shape[0] #720 
        self.imageWidth = self.image.shape[1] #1280 

    def show(self):
        cv2.cv2.imshow("res", self.line_image) #self.line_image)


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
                print(e)
            

    def Do(self):
        self.canny()
        self.cropImage()
        self.makeLines()
        self.debugLine()
        self.newDisplayer()
        self.averageLines()
        self.lineCorrection()
        
        #self.debug()


    def debug(self):
        try:
            foo = self.leftFitAVG - self.rightFitAVG
            cv2.line(self.line_image, (640,720), (640-10*foo,0),(255,0,0),self.line_thickness ) #(lx1,ly1), (lx2,ly2), self.lineColor[lcolor], self.line_thickness)
        except Exception as e:
            print(e)

        




#and self.foo == 0:    # slope, intercept
        # try:
        #     bar = abs(self.parametersLeft[self.parCounter-1][0])/abs(self.parametersRight[self.parCounter-1][0]) 
        # except Exception as e:
        #     #print(e)
        #     bar = 0






#video 
cap = cv2.VideoCapture(path)
_, startImage = cap.read()
visor = visor(colorimage = startImage)
grab.grab()
while (cap.isOpened()):
    _, image = cap.read()
    visor.updateImage(image)
    visor.Do()
    visor.show()

    if cv2.waitKey(16) == ord('q'):
         break




#############################################screen capture
# startImage = grab.grab()
# visor = visor(colorimage = startImage)

# while True:
#     image = grab.grab()
#     visor.updateImage(image)
#     visor.Do()
#     visor.show()
#     if cv2.waitKey(1) == ord('q'):
#         break




#static picture
import cv2
import matplotlib.pyplot as plt
import numpy as np
#"C:/car vision proj/media/scr.jpg"
path = "C:/car vision proj/media/DR101423.AVI"
#path = "D:/ets2.mp4"
class visor():
    def __init__(self, colorimage):
        if type(colorimage) == type("sample"):
            self.colorimage = cv2.imread(colorimage)
            
        else:
            self.colorimage = colorimage
        
        self.image = cv2.cvtColor(self.colorimage, cv2.COLOR_RGB2GRAY)
        self.lineColor = (255,0,0)
        self.line_thickness = 2 
        self.canny_treshold = (50, 150)
        #self.polygons = [[(0, 719), (1280,719),(970,550), (420,550)]]
        self.polygons = [[(200,720),(1100,720),(800,540),(580,540)]]#ETS STANDART BUMPER
        #self.polygons = polygons = [[(0, 719), (1280,719),(1280,0), (0,0)]] #full
        
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
        self.DoDisplayVerticalLine = False
    
    def canny(self):
        blur = cv2.GaussianBlur(self.image ,(7,7),0)
        self.canny_image = cv2.Canny(blur, self.canny_treshold[0], self.canny_treshold[1])


    def cropImage(self):
        polygon = np.array(self.polygons)
        mask = np.zeros_like(self.image)
        cv2.fillPoly(mask, polygon, 100)
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
        return np.array([x1,y1, x2,y2])


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

    # def updateParameters(self):
    #     if self.parCounter < 10:
    #         self.parametersLeft[self.parCounter] = self.leftFitAVG
    #         self.parametersRight[self.parCounter] = self.rightFitAVG
    #         self.parCounter += 1
    #     else:
    #         self.parCounter = 0
    #         self.parametersLeft[self.parCounter] = self.leftFitAVG
    #         self.parametersRight[self.parCounter] = self.rightFitAVG
    #         self.parCounter += 1

    def updateImage(self, colorimage):
        self.colorimage = colorimage
        self.image = cv2.cvtColor(self.colorimage, cv2.COLOR_RGB2GRAY)
        self.imageHeight = self.image.shape[0] #720 
        self.imageWidth = self.image.shape[1] #1280 

    def show(self, delay, cap):
        cv2.cv2.imshow("res",self.line_image)
        if cv2.waitKey(0) == ord('q'):
            cap.release()
            cv2.destroyAllWindows()


    def DifferenseBetweenLines(self):
        if self.averegedLines[1][0] !=0 and self.averegedLines[0][0] !=0:
            print((self.averegedLines[1][0]+self.averegedLines[0][0]), '\n')

            

    def Do(self):
        self.canny()
        self.cropImage()
        self.makeLines()
        self.displayLines()
        self.averageLines()

        #self.updateParameters()
        #self.DifferenseBetweenLines()
        
#and self.foo == 0:    # slope, intercept
        try:
            bar = abs(self.parametersLeft[self.parCounter-1][0])/abs(self.parametersRight[self.parCounter-1][0]) 
        except Exception as e:
            #print(e)
            bar = 0
        #print(bar)
            #self.foo+=1







cap = cv2.VideoCapture(path)
_, startImage = cap.read()
visor = visor(colorimage = startImage)
while (cap.isOpened()):
    _, image = cap.read()
    visor.updateImage(image)
    visor.Do()
    visor.show(delay = 1, cap = cap)



# visor = visor(colorimage = "C:/car vision proj/media/scr.jpg")

# visor.Do()

# print(visor.averegedLines)
# visor.show()


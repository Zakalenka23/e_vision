import cv2
import matplotlib.pyplot as plt
import numpy as np

#visuals
lineColor = (255,0,0)



#constants
line_thickness = 2 
canny_trashold = (50, 150)
polygons = [[(0, 719), (1280,719),(970,550), (420,550)]] #(640,360)]
#polygons = polygons = [[(0, 719), (1280,719),(870,550), (520,550)]]
houhgVoteTrashold = 75



#Определение линий
def canny(image, trashhold):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(7,7),0)
    canny_image = cv2.Canny(blur, trashhold[0], trashhold[1])
    return canny_image

#отрисовка изображения линий на черную копию исходного изображения
def display_lines(image, lines, line_thickness, lineColor):
    line_image = np.copy(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2,y2 = line.reshape(4)
            try:
            	cv2.line(line_image, (x1,y1), (x2,y2), lineColor, line_thickness)
            except Exception as e:
                print(e, "\n")
            	
    return line_image


#region_of_interest - обрезание картинки по маске, которая делается по полигу
def ROI(image, polygons):
    height = image.shape[0]
    triangle = np.array(polygons)
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, triangle, 100)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image
    #return mask

def make_coordinates(image, line_parameters):
    slope, intercept = line_parameters
    y1 = image.shape[0]
    y2 = int(y1*(3/5))
    x1 = int((y1 - intercept)/slope) 
    x2 = int((y2 - intercept)/slope) 
    return np.array([x1,y1, x2,y2])

def average_slope_intercept(image, lines):
    left_fit = []
    right_fit = []
    leftSlope = []
    rightSlope = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            parameters = np.polyfit((x1,x2), (y1,y2), 1)
            print (parameters, '\n')
            slope = parameters[0]
            intercept = parameters[1]
            if slope < -0.5:
                left_fit.append((slope, intercept))
                leftSlope.append(slope)
            elif slope > 0.5:
                right_fit.append((slope, intercept))
                rightSlope.append(slope)
        left_fit_average = np.average(left_fit, axis=0)    
        right_fit_average = np.average(right_fit, axis=0) 
        #print(left_fit_average)
        # try:
        #     AVGleftSlope = np.average(leftSlope)
        # except Exception as e:
        #     AVGleftSlope = 0
        #     print("AVGleftSlope = np.average(leftSlope)")
        
        # try:
        #     AVGrightSlope = np.average(rightSlope)
        # except Exception as e:
        #     AVGrightSlope = 0
        #     print("AVGrightSlope = np.average(rightSlope)")
        
        try:
            left_line = make_coordinates(image, left_fit_average)
        except Exception as e:

            print(e, '\n')
            left_line = np.array([0,0,0,0])             
        try:
            right_line = make_coordinates(image, right_fit_average)
        except Exception as e:
            print(e, '\n')
            right_line = np.array([0,0,0,0])

        return  np.array([left_line, right_line]) #np.array(AVGleftSlope, AVGrightSlope),
                   

def AVGlinesInTime(avgLines):
    if avgLines is not None:
        pass
    pass



def main():
    cap = cv2.VideoCapture("DR101423.AVI")

    while(cap.isOpened()):
        _, image = cap.read()
        #загружаем картинку из файла
        #aimage = cv2.imread("vert.jpg")
        #image = cv2.imread("test.jpg")
        #Ищем линии и делаем из них точки
        canny_image = canny(image, canny_trashold)
        #Обрезаем картинку до нужной нам области
        cropped_image = ROI(canny_image, polygons)
        cv2.imshow("new",cropped_image)
        #Проходимся по массиву точек и делаем из него линии
        lines = cv2.HoughLinesP(cropped_image,5,np.pi/360, houhgVoteTrashold, minLineLength=5, maxLineGap=30)
        #print("HOUGHLINES",cv2.HoughLines(cropped_image,0.1,np.pi/180,houhgVoteTrashold), "\n\n\n")
        
        #print(lines) 
        #DEBUG
        imageWithRawLines = display_lines(image, lines, line_thickness, lineColor)

        avereged_lines = average_slope_intercept(image, lines)


        #AVGlinesInTime(avereged_lines)

        #накладываем линии на наше изображение, если они есть
        image_with_lines = display_lines(image, avereged_lines, line_thickness, lineColor)
        cv2.imshow("res",imageWithRawLines)
        # cv2.imshow("new",canny_image)
        cv2.imshow("new",image_with_lines)
        
        if cv2.waitKey(0) == ord('q'):
            cv2.destroyAllWindows()  
            break


if __name__ == "__main__":
    main()
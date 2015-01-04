import cv2
import numpy as np
import copy
import time
import sys
import subprocess
import os

os.system("rm ./Frames/*")

interval = 0.00

h_min = 0
h_max = 120

y_min = 0

pausa_dopo_cambio = 0.0

frame_number = 0

gioca = True

def click_destra(p):
    p.stdin.write("cat /sdcard/click_destra > /dev/input/event2\n")
    
def click_sinistra(p):
    p.stdin.write("cat /sdcard/click_sinistra > /dev/input/event2\n")
    
def click_centro(p):
    p.stdin.write("cat /sdcard/click_centro > /dev/input/event2\n")

p = subprocess.Popen(["adb", "shell"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)


            
def create_blank(width, height, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB"""
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color

    return image

def nothing(x):
    pass
    
r1 = [145, 252, h_min, h_max]#287]
r2 = [372, 487, h_min, h_max]#287]

def filtra_ostacoli(c):

    buoni = []
    
    for cnt in c:
        x,y,w,h = cv2.boundingRect(cnt) 
        print w
        if y+h/2 > y_min:
            
            if w * h > 800 and w > 50:
                buoni.append(cnt)
            
    return buoni   
    
def ostacoli(frame):
    
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(img,59,76, apertureSize = 3)
    #edges = cv2.GaussianBlur(edges,(5,5),5)
    
    kernel = np.ones((14,14),np.uint8)
    #edges = cv2.erode(edges,kernel,iterations = th1)
    #edges = cv2.dilate(edges,kernel,iterations = th1)       
    #edges = cv2.erode(edges,kernel,iterations = th2)
    
    
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    edges = cv2.erode(edges,kernel,iterations = 2)
    
    #cp = copy.deepcopy(edges)
    
    cp1 = edges[r1[2]:r1[3],r1[0]:r1[1]]
    
    cp2 = edges[r2[2]:r2[3],r2[0]:r2[1]]
    
    contours1,hierarchy = cv2.findContours(cp1, 1, 2)
    contours2,hierarchy = cv2.findContours(cp2, 1, 2)
    
    contours1 = filtra_ostacoli(contours1)
    contours2 = filtra_ostacoli(contours2)
    
    return (contours1, contours2)

#image window
cv2.namedWindow('res')

#loading images
cap = cv2.VideoCapture(1)

tic = time.time()



posizione = "sx"

while True:
    _, img = cap.read()
    
    frame = img
    
    (rows,cols, depth) = img.shape
    M = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
    img = cv2.warpAffine(img,M,(cols,rows))
    
    frame = img
       
    a = ostacoli(frame)
    b = ostacoli(frame)
    c = ostacoli(frame)
    
    
    sx = [len(a[0]), len(b[0])]#, len(c[0])]
    dx = [len(a[1]), len(b[1])]#, len(c[1])]
    
    m_sx = np.mean(sx)
    m_dx = np.mean(dx)
    
    #print m_sx, m_dx
      
    for cnt in a[0]:
        x,y,w,h = cv2.boundingRect(cnt)
        x_mid = x + w/2
        y_mid = y + h/2
        
        x += r1[0]
        y += r1[2]
        
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
    
    for cnt in a[1]:
        x,y,w,h = cv2.boundingRect(cnt)
        x_mid = x + w/2
        y_mid = y + h/2
        
        x += r2[0]
        y += r2[2]
        
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        
        if x_mid < 300:
            libero_sx = False
        else:
            libero_dx = False    
        
           
    cv2.rectangle(img,(r1[0],r1[2]),(r1[1],r1[3]),(0,0,255),2)
    cv2.rectangle(img,(r2[0],r2[2]),(r2[1],r2[3]),(0,0,255),2)    
   
    #press ESC to stop
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
        
    if gioca:
    
        if posizione == "sx":
            if m_sx < 0.1:
                click_sinistra(p)
                posizione = "sx"
                time.sleep(interval)
                cv2.putText(img,"sx", (0,400), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
            else:
                click_destra(p)
                posizione = "dx"
                cv2.putText(img,"dx", (0,400), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
        else:
            if m_dx < 0.1:
                click_destra(p)
                posizione = "dx"
                time.sleep(interval)
                cv2.putText(img,"dx", (0,400), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
            else:
                click_sinistra(p)
                posizione = "sx"
                cv2.putText(img,"sx", (0,400), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
     
    
     #show the image
    cv2.imshow("originale", img)
    #cv2.imshow('res',edges)
    
    cv2.imwrite("./Frames/" + str(frame_number) + ".png", img)
    
    frame_number += 1
    
    time.sleep(interval)

cv2.destroyAllWindows()

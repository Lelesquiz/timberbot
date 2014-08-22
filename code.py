import cv2
import numpy as np
import copy
import time
import sys
import subprocess
import math

def ruotata(img):
    (rows,cols, depth) = img.shape
    M = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
    img = cv2.warpAffine(img,M,(cols,rows))
    
    return img

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
    
def valori_box(cap, durata):
    valori_dx = []
    valori_sx = []

    # calibro a sinistra
    start = time.time()
    while (time.time() - start) < durata:
        _, frame = cap.read()
        
        frame = ruotata(frame)
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
        l = 100
        
        h = 150
        
        xl = 150
        y = 240
        
        xr = 380
           
        cv2.rectangle(frame,(xl,y),(xl+l,y+h),(0,0,255),2) 
        cv2.rectangle(frame,(xr,y),(xr+l,y+h),(0,0,255),2)
        
        box_l = frame[y:y+h,xl:xl+l] 
        box_r = frame[y:y+h,xr:xr+l]   
        
        s_l = np.sum(box_l)
        s_r = np.sum(box_r)
        
        print s_l, s_r 
        
        valori_sx.append(s_l)
        valori_dx.append(s_r)
        
        #show the image
        #cv2.imshow("originale", frame)
        cv2.imshow('res',frame)
       
        #press ESC to stop
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
            
            
    valori_dx = np.array(valori_dx)
    valori_sx = np.array(valori_sx)

    m_dx = np.mean(valori_dx)
    std_dx = np.std(valori_dx)

    m_sx = np.mean(valori_sx)
    std_sx = np.std(valori_sx)

    return (m_sx, m_dx, std_sx, std_dx)   

#loading images
cap = cv2.VideoCapture(1)

_, f0 = cap.read()

f0 = ruotata(f0)

f0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)

medie = []
std = []

valori_box(cap, 5.0)


      
(m_sx, m_dx, std_sx, std_dx) = valori_box(cap, 1.0)

medie.append(m_sx)
medie.append(m_dx)

std.append(std_sx)
std.append(std_dx)

click_destra(p)


valori_box(cap, 1.5)

(m_sx, m_dx, std_sx, std_dx) = valori_box(cap, 1.0)

medie.append(m_sx)
medie.append(m_dx)

std.append(std_sx)
std.append(std_dx)


tic = time.time()
while True:

    (m_sx, m_dx, std_sx, std_dx) = valori_box(cap, 0.1)
    
    sig = [math.fabs(medie[0] - m_sx) / std[0],
           math.fabs(medie[1] - m_dx) / std[1],
           math.fabs(medie[2] - m_sx) / std[2],
           math.fabs(medie[3] - m_dx) / std[3]]
    
    minimo = 10**9
    
    pos_minimo = 0
        
    for i in range(len(sig)):
        if sig[i] < minimo:
            minimo = sig[i]
            pos_minimo = i
           
    print minimo, pos_minimo
    
    if minimo < 1.0:            
        if pos_minimo % 2 == 0:
            click_sinistra(p)
        else:
            click_destra(p)
        time.sleep(0.000)
              
        
cv2.destroyAllWindows()

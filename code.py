import cv2
import numpy as np
import copy
import time
import sys
import subprocess
import math

# CHANGE THIS VALUES IN ORDER TO ACHIEVE GOOD RESULTS.
# THEY DEPEND OR YOUR PARTICULAR DEVICE AND WEBCAM POSITION
# TUNE THEM UNTIL THE BOT WORKS PROPERLY
 
# width of the boxes    
l = 100
# heigth of the boxes
h = 150
# x value of top left corner of left box
xl = 150
# y value of top part of the boxes
y = 240
# y value of top left corner of right box
xr = 380


# rotates the image
def rotated(img):
    (rows,cols, depth) = img.shape
    M = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
    img = cv2.warpAffine(img,M,(cols,rows))
    return img
    
# INPUT TO THE PHONE IS ACHIEVED BY DIRECTLY WRITING 
# INTO THE TOUCHSCREEN DEVICE BUFFER A PREVIOUSLY RECORDED
# TAP EVENT. 
# IN EXAMPLE SEE THIS POST 
# http://stackoverflow.com/questions/19063057/android-simulate-fast-swipe/19127078#19127078

# performs a tap on the right part of the screen
def right_click(p):
    p.stdin.write("cat /sdcard/right_clic > /dev/input/event2\n")

# performs a tap on the left part of the screen   
def left_click(p):
    p.stdin.write("cat /sdcard/left_clic > /dev/input/event2\n")

# performs a tap on the center part of the screen    
def center_click(p):
    p.stdin.write("cat /sdcard/center_click > /dev/input/event2\n")

# creates new image(numpy array) filled with certain color in RGB          
def create_blank(width, height, rgb_color=(0, 0, 0)):
    
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)
    
    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    
    # Fill image with color
    image[:] = color
    
    return image

# computes the sum of the pixel inside the top region of the screen
# returns (m_sx, m_dx, std_sx, std_dx), averages and stds
def valori_box(cap, duration):
    
    # lists to store the values
    valori_dx = []
    valori_sx = []

    start = time.time()
    while (time.time() - start) < duration:
        _, frame = cap.read()
        
        frame = rotated(frame)
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
         
        
        global l, h, xl, y, xr 
        
        # GO TO THE TOP OF THE SCRIPT AND TUNE THIS VARIABLES
        """
        l = 100
        # heigth of the boxes
        h = 150
        # x value of top left corner of left box
        xl = 150
        # y value of top part of the boxes
        y = 240
        # y value of top left corner of right box
        xr = 380
        """
        
        # draw a red rectangle on the frame   
        cv2.rectangle(frame,(xl,y),(xl+l,y+h),(0,0,255),2) 
        cv2.rectangle(frame,(xr,y),(xr+l,y+h),(0,0,255),2)
        
        # left box
        box_l = frame[y:y+h,xl:xl+l] 
        # right box
        box_r = frame[y:y+h,xr:xr+l]   
        
        # left sum
        s_l = np.sum(box_l)
        # right sum
        s_r = np.sum(box_r)
        
        # optional
        print s_l, s_r 
        
        # store the value
        valori_sx.append(s_l)
        valori_dx.append(s_r)
        
        # show the image
        cv2.imshow('res',frame)
       
        # press ESC to stop
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
            
    # convert to numpy arrays        
    valori_dx = np.array(valori_dx)
    valori_sx = np.array(valori_sx)

    # compute the averages and stds
    m_dx = np.mean(valori_dx)
    std_dx = np.std(valori_dx)
    m_sx = np.mean(valori_sx)
    std_sx = np.std(valori_sx)

    return (m_sx, m_dx, std_sx, std_dx) 


# open an adb shell in order to provide screen input
# using right_click, left_click, center_click
p = subprocess.Popen(["adb", "shell"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)    

# open the webcam
cap = cv2.VideoCapture(1)

# read the first frame
_, f0 = cap.read()

# rotate it
f0 = rotated(f0)

# convert to greyscale image
f0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)

# lists to store averages and standard deviations
averages = []
std = []

# not really needed, but very handful to properly position webcam
# and start the capture/display
valori_box(cap, 5.0)

# click in order to exit the main menu and enter the game
right_click(p)

# compute the calibration values
(m_sx, m_dx, std_sx, std_dx) = valori_box(cap, 1.0)

# store them
averages.append(m_sx)
averages.append(m_dx)
std.append(std_sx)
std.append(std_dx)

# YES, DO IT TWICE
# compute the calibration values
(m_sx, m_dx, std_sx, std_dx) = valori_box(cap, 1.0)

# store them
averages.append(m_sx)
averages.append(m_dx)
std.append(std_sx)
std.append(std_dx)

# start the main routine

tic = time.time()
while True:
    
    # compute the pixel sum of the two boxes
    (m_sx, m_dx, std_sx, std_dx) = valori_box(cap, 0.1)
    
    # compute the relative distance between the actual values
    # and the calibration ones
    sig = [math.fabs(averages[0] - m_sx) / std[0],
           math.fabs(averages[1] - m_dx) / std[1],
           math.fabs(averages[2] - m_sx) / std[2],
           math.fabs(averages[3] - m_dx) / std[3]]
    
    # value used as infinite
    # (used to check minimum)
    minimo = 10**9
    
    # position of minimum sig
    pos_minimo = None
        
    # get minimum    
    for i in range(len(sig)):
        if sig[i] < minimo:
            minimo = sig[i]
            pos_minimo = i
           
    print minimo, pos_minimo
    
    # THIS IS THE KEY POINT: click left or right depending on the closest value
    if minimo < 1.0:   
        
        if pos_minimo % 2 == 0:
            # in this case the left part of the screen is not occupied by a branch
            # then it is to be sent a left click
            # NOTE THAT IT IS NOT IMMEDIATE, SO IT IS IMPORTANT TO TUNE 
            # THE PARAMETERS INSIDE "valori_box" IN ORDER TO HANDLE
            # THE DELAY BETWEEN SENDING THE COMMANDS AND THE RESPONSE BY THE PHON
            left_click(p)
        else:
            # as above but with right click
            right_click(p)
            
        # not sure why i put it, but it works 
        time.sleep(0.000)
              
# close the display window and exit        
cv2.destroyAllWindows()

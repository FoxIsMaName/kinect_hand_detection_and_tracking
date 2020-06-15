from multiprocessing import Process, current_process, cpu_count, Queue, Pool
from threading import Thread, current_thread
import time
import datetime
import numpy as np
from timeit import default_timer as timer
import cv2
import os

result = []

loop = 10000

def get_contour(xsize,ysize):

    img = cv2.imread('test.jpg')
    for i in range(loop):
        img = cv2.resize(img, (xsize,ysize))
        imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        imgray = cv2.GaussianBlur(imgray, (5,5), 0)
        imgray = cv2.erode(imgray, None, iterations=1)
        imgray = cv2.dilate(imgray, None, iterations=1)
        ret,thresh = cv2.threshold(imgray,127,255, cv2.THRESH_BINARY)
        _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours

def get_input():
    global xsize,ysize
    pygame_refresh(xsize,ysize)

def pygame_refresh(xsize,ysize):
    cs = get_contour(xsize,ysize)

def keymap():
    # print("PID: %s, Process Name: %s, Thread Name: %s" % (
    #     os.getpid(),
    #     current_process().name,
    #     current_thread().name)
    # )
    cs = get_input()

xsize,ysize = 150,150

if __name__ == '__main__':

    #--------------------------------- Prototype Image Processing -----------------------------

    for i in range(50):

        start = time.clock()
        s_timer = timer()

        th1 = Thread(target=keymap)
        th1.start()
        th1.join()

        # print("Thread Full image processing time : %s \n" % (time.clock()-start))
        # print("Thread Full image processing time : %s \n" % (timer()-s_timer))

        file = open("clock time thread.csv","a")
        file.write(str(datetime.datetime.now()) + "," + str(time.clock()-start) + "," + str(timer()-s_timer) + "\n")
        file.close()

        print("Test %s complete." %(i))

    #--------------------------------- End Prototype Image Processing -------------------------

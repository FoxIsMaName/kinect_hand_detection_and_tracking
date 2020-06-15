from multiprocessing import Process, current_process, Queue
from threading import current_thread
import time
import datetime
import numpy as np
from timeit import default_timer as timer
import cv2
import os

def convert_col(image):
    for i in range(loop):
        data = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return data

def gaussian(image):
    for i in range(loop):
        data = cv2.GaussianBlur(image, (5, 5), 0)
    return data

def erosion(image):
    for i in range(loop):
        data = cv2.erode(image, None, iterations=1)
    return data

def dilation(image):
    for i in range(loop):
        data = cv2.dilate(image, None, iterations=1)
    return data

def threshold(image):
    for i in range(loop):
        ret, thresh = cv2.threshold(image, 127, 255, 0)
    return thresh

def find_contours(q2,q3):
    thresh_hold = q2.get()
    for i in range(loop):
        _, cs, _ = cv2.findContours(thresh_hold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    q3.put(cs)

def group1(img,q1):
    # print("PID: %s, Process Name: %s, Thread Name: %s" % (
    #     os.getpid(),
    #     current_process().name,
    #     current_thread().name)
    #       )
    data = convert_col(img)
    data = gaussian(data)
    q1.put(data)

def group2(q1,q2):
    # print("PID: %s, Process Name: %s, Thread Name: %s" % (
    #     os.getpid(),
    #     current_process().name,
    #     current_thread().name)
    #       )
    img = q1.get()
    data = erosion(img)
    data = dilation(data)
    thresh = threshold(data)
    q2.put(thresh)

result = []
xsize, ysize = 150, 150
loop = 10000

if __name__ == '__main__':

    im_array = []
    im = cv2.imread('test.jpg')
    im = cv2.resize(im, (150, 150))

    imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    q1 = Queue()
    q2 = Queue()
    q3 = Queue()

    for i in range(50):

        start = time.clock()
        s_timer = timer()

        p0 = Process(target=group1, args=(im,q1,))
        p1 = Process(target=group2, args=(q1,q2,))
        p2 = Process(target=find_contours, args=(q2,q3,))

        p0.start()
        p1.start()
        p2.start()

        p0.join()
        p1.join()
        p2.join()

        q3.get()

        # print("Multiprocessing test time : %s" %(time.clock()-start))
        # print("Multiprocessing test time : %s" %(timer()-s_timer))

        file = open("clock time multiprocessing.csv","a")
        file.write(str(datetime.datetime.now()) + "," + str(time.clock()-start) + "," + str(timer()-s_timer) + "\n")
        file.close()

        print("Test %s complete." %(i))

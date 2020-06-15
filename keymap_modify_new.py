from freenect import sync_get_depth as get_depth
import numpy as np
import cv2
import math
import os
import pygame
import time
from timeit import default_timer as timer
import datetime
from multiprocessing import Process, current_process, cpu_count, Pool, Lock, Queue
# import webbrowser
from pynput.keyboard import Key, Controller as keyboard_con
from pynput.mouse import Button, Controller as mouse_con
# from Queue import Queue as queue
# from threading import Thread, Lock

BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
PURPLE = (255,0,255)
BLUE = (0,0,255)
WHITE = (255,255,255)
YELLOW = (255,255,0)

class BlobAnalysis:
    def __init__(self,contour):
        self.contour = contour
        self.contour_s = np.vstack(contour).squeeze()
        self.contour_point = self.get_contour_point()
        self.centroid = self.get_centroid()
        self.convex_hull = self.get_convex_hull()
        self.approx_hull_count = self.get_approx_hull_count()
        self.id = -1
        self.area = cv2.contourArea(self.contour)
        self.deflect_count_90 = self.get_deflect_count(90)
        self.isHand = self.check_isHand()
        self.isGrab = self.isGrab()
    
    def set_id(self,i):
        self.id = i
    
    def get_contour_point(self):
        return np.array(self.contour_s).tolist()
    
    def get_centroid(self):
        m = cv2.moments(self.contour)
        cX = int(m['m10'] / m['m00'])
        cY = int(m['m01'] / m['m00'])
        return (cX, cY)
    
    def get_convex_hull(self):
        convexHull = cv2.convexHull(self.contour)
        epsilon = 0.015*cv2.arcLength(convexHull,True)
        approx = cv2.approxPolyDP(convexHull,epsilon,True)
        approx = np.vstack(approx).squeeze()
        return np.array(approx).tolist()
    
    def get_approx_hull_count(self):
        approx = self.convex_hull
        return len(approx)
    
    def get_deflect_count(self,max_angle):
        count = 0
        hull = cv2.convexHull(self.contour,returnPoints = False)
        defects = cv2.convexityDefects(self.contour, hull)
        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]
            start = self.contour_s[s]
            end = self.contour_s[e]
            far = self.contour_s[f]
            a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
            angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57
            if angle <= max_angle:
                count += 1
        return count
    
    def check_isHand(self):
        if self.deflect_count_90 == 4 :
            return True
        else:
            return False
    
    def set_isHand(self,logic):
        self.isHand = logic

    def set_isGrab(self,logic):
        self.isGrab = logic
    
    def isGrab(self):

        # contourArea = int(cv2.contourArea(cv2.convexHull(self.contour)))
        # oldArea = int(self.area)
        # # print("This is new area ",(0.7*contourArea), "This is old area", oldArea)
        # if oldArea > int(0.7*contourArea) and oldArea < 1200 and oldArea > 600:
        #     #print("Hand is Grab")
        #     return True
        # else:
        #     return False

        if self.deflect_count_90 == 0 :
            return True
        else:
            return False

    def isNear(self,ref):
        (x1,y1) = self.centroid
        (x2,y2) = ref.centroid
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist < 50:
            return True
        else:
            return False
    
    def isSame(self,ref):
        if self.isNear(ref):
            if self.area < 1.5*ref.area or self.area < 0.1*ref.area:
                return True
            else:
                return False
        else:
            return False

def blobs_track(blobs,blob,i,n):
    # global blobs
    global blobs_movement
    if blobs_buffer[n] == []:
        if n+1 < buffer_size:
            blobs_track(blobs,blob,i,n+1)
        else:
            blob.set_id(i)
            blobs_movement[i] = [blob.centroid,blob.centroid]
    else:
        for j in range(len(blobs_buffer[n])):
            if blob.isSame(blobs_buffer[n][j]):
                new_id = blobs_buffer[n][j].id
                exist = False
                for k in blobs:
                    if k.id == new_id:
                        exist = True
                if exist:
                    if n+1 < buffer_size:
                        blobs_track(blobs,blob,i,n+1)
                    else:
                        new_id = 1
                        for k in range(buffer_size):
                            if max(old_id[k]or[0])+1 > new_id:
                                new_id = max(old_id[k])+1
                        blob.set_id(new_id)
                        old_id[0].append(new_id)
                        blobs_movement[new_id] = [blob.centroid,blob.centroid]
                else:
                    
                    blob.set_id(new_id)
                    blobs_movement[new_id].append(blob.centroid)
                    blobs_movement[new_id] = blobs_movement[new_id][-20:]

                if blob.id != -1:
                    break
        if blob.id == -1:
            if n+1 < buffer_size:
                blobs_track(blobs,blob,i,n+1)
            else:
                new_id = 1
                for k in range(buffer_size):
                    if max(old_id[k]or[0])+1 > new_id:
                        new_id = max(old_id[k])+1
                blob.set_id(new_id)
                old_id[0].append(new_id)
                blobs_movement[new_id] = [blob.centroid,blob.centroid]
    return blob

def check_gesture(fps):
    global blobs
    global blobs_movement
    n_blobs = len(blobs)
    id_hand = []
    id_grab = []
    for blob in blobs:
        if blob.isHand:
            id_hand.append(blob.id)
            id_grab = []
        elif blob.isGrab:
            id_grab.append(blob.id)
            id_hand = []
    n_hand = len(id_hand)
    n_grab = len(id_grab)

    if n_hand == 0 and n_grab == 0:
        return "undefined action"

    elif n_hand == 1:
        n_frames = int(fps)+1
        vector_hand = blobs_movement[id_hand[0]][-n_frames:]
        weight = {"swipe up":0,"swipe down":0,"swipe left":0,"swipe right":0}

        for i in range(len(vector_hand)):
            if i == 0 :
                (x0,y0) = vector_hand[0]
            else:
                (x1,y1) = vector_hand[i]
                radian = math.atan2(y1-y0,x1-x0)
                degree = math.degrees(radian)
                dist = math.hypot(x1-x0,y1-y0)
                if dist > 8:
                    if degree>-135 and degree<-45:
                        weight["swipe up"] += 1
                    if degree>45 and degree<135:
                        weight["swipe down"] += 1
                    if degree>135 or degree<-135:
                        weight["swipe left"] += 1
                    if degree>-45 and degree<45:
                        weight["swipe right"] += 1
                (x0,y0) = (x1,y1)
        ans = "" + max(weight, key=weight.get)
        p70 = (7/10)*(n_frames-1)
        if weight[ans] > p70 :
            return ans
        else :
            return "undefined action"

    elif n_grab == 1:
        n_frames = int(fps)+1
        vector_grab = blobs_movement[id_grab[0]][-n_frames:]
        weight = {"grab up":0,"grab down":0,"grab left":0,"grab right":0}
        for i in range(len(vector_grab)):
            if i == 0 :
                (x0,y0) = vector_grab[0]
            else:
                (x1,y1) = vector_grab[i]
                radian = math.atan2(y1-y0,x1-x0)
                degree = math.degrees(radian)
                dist = math.hypot(x1-x0,y1-y0)
                if dist > 8:
                    if degree>-135 and degree<-45:
                        weight["grab up"] += 1
                    if degree>45 and degree<135:
                        weight["grab down"] += 1
                    if degree>135 or degree<-135:
                        weight["grab left"] += 1
                    if degree>-45 and degree<45:
                        weight["grab right"] += 1
                (x0,y0) = (x1,y1)
        ans = "" + max(weight, key=weight.get)
        p70 = (7/10)*(n_frames-1)
        if weight[ans] > p70 :
            return ans
        else :
            return "undefined action"

blobs = []
buffer_size = 3
blobs_buffer = [[]] * buffer_size
old_id = [[]] * buffer_size
blobs_movement = {}
fps = 0
state = 0
last_gesture = "undefined action"
t0 = time.time()
tt0 = t0
tt1 = t0
used_time = 0
c = 0
start_time = timer()
keyboard = keyboard_con()
mouse = mouse_con()
undefined_count = 0     # use to count undefined action
state_gesture = ""      # use to save state of gesture to check

def get_contours_new(q1,q2,lock):

    while True:
        # update_id(lock)
        # print("Process 1 start \n")
        start = time.clock()
        global xsize,ysize
        (depth,_) = get_depth()
        # for i in range(100):
        depth = depth.astype(np.float32)
        depth = cv2.flip(depth, 1)
        depth = cv2.resize(depth,(xsize,ysize))
        depth = cv2.GaussianBlur(depth, (5,5), 0)

        depth = cv2.erode(depth, None, iterations=1)
        depth = cv2.dilate(depth, None, iterations=1)
        min_hand_depth = np.amin(depth)-10
        hand_depth = 80
        max_hand_depth = min_hand_depth + hand_depth
        if max_hand_depth > 700 :
            max_hand_depth = 700
        (_,BW) = cv2.threshold(depth, max_hand_depth, min_hand_depth, cv2.THRESH_BINARY_INV)
        BW = cv2.convertScaleAbs(BW)
        #BW = cv2.resize(BW,(xsize,ysize))
        _,cs,_ = cv2.findContours(BW,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cs_f = []
        for i in range(len(cs)):
            if cv2.contourArea(cs[i]) > 500:
                cs_f.append(cs[i])
        del depth,BW
        clock_time = time.clock()-start
        lock.acquire()
        q1.put(cs_f)
        q2.put(clock_time)
        lock.release()
        # print("image processing time : %s \n" %(clock_time))
        # return cs_f

def update_id():

    # while True:
    # start = timer()
    # lock.acquire()
    global blobs
    # blobs = q_blobs.get()
    blobs = []
    global blobs_buffer
    global old_id
    # print("start update id")
    for i in range(buffer_size):
        old_id[i] = []
        for j in range(len(blobs_buffer[i])):
            old_id[i].append(blobs_buffer[i][j].id)
    # lock.release()
    # q_blobs.put(blobs)
    # print("update id time : %s \n" %(timer()-start))

    # return blobs

# def blob_tracking(cs,blobs,state):
def blob_tracking(q1,q2,lock):

    while True:
        # print("Process 2 start \n")
        start = time.clock()
        global blobs
        # blobs = update_id(blobs)
        # blobs = q_blobs.get()

        global blobs_buffer

        # blobs = update_id(blobs)
        update_id()

        # lock.acquire()
        cs = q1.get()
        # lock.release()
        # print("start blob tracking")

        # lock.acquire()
        for i in range(len(cs)):
            blob = BlobAnalysis(cs[i])
            blob = blobs_track(blobs,blob,i,0)
            blobs.append(blob)

        # print(blobs)

        for i in range(buffer_size):
            if i == 0:
                blobs_buffer[i] = blobs
            else:
                blobs_buffer[i] = blobs_buffer[i-1]

        # lock.release()

        # state = keymap_new(blobs,state)
        img_pro_time = q2.get()
        get_gesture(start,img_pro_time)

        # blob_time = time.time()-start
        # img_pro_time = q2.get()
        # print("blob tracking time : %s \n" %(blob_time))

        # full_process_time = img_pro_time+blob_time

        # print("full process time : %s \n" %(full_process_time))

        # print("write row")
        # file = open("time pipeline thread.csv","a")
        # file.write(str(datetime.datetime.now()) + "," + str(full_process_time) + "\n")
        # file.close()

        # return blobs,state

def show_page():
    # os.system("sleep 5")
    os.system("chromium-browser -no-sandbox --app=file:///home/pi/Desktop/kinect_hand_detection_and_tracking_2/src/index.html")
    # webbrowser.open('file://' + os.path.realpath("/home/scarletdragon/Desktop/kinect_hand_detection_and_tracking_2/src/index.html"))
    # keyboard.press(Key.f11)
    # keyboard.release(Key.f11)

# def keymap_new(blobs,state):

def key_mapping(gesture):

    if gesture == "swipe up":
        mouse.scroll(0 , -5)
    if gesture == "swipe down":
       mouse.scroll(0 , 5)
    if gesture == "swipe left":
        keyboard.press(Key.right)
        keyboard.release(Key.right)
    if gesture == "swipe right":
        keyboard.press(Key.left)
        keyboard.release(Key.left)

    if gesture == "grab down":
        keyboard.press('x')
        keyboard.release('x')
        # print("Grab up")
    if gesture == "grab left" :
        keyboard.press('z')
        keyboard.release('z')
        # print("Grab left")
    if gesture == "grab right" :
        keyboard.press('c')
        keyboard.release('c')               
        # print("Grab right")

def get_gesture(start,img_pro_time):

    global fps
    global last_gesture
    global t0,tt0,tt1,used_time,c,start_time
    global state
    global undefined_count
    global state_gesture

    if state == 0:
        t0 = time.time()
        tt0 = t0
        tt1 = t0
        used_time = 0
        c = 0
        start_time = timer()

        undefined_count = 0     # use to count undefined action
        state_gesture = ""      # use to save state of gesture to check

        # print("start state")
        state = 1

    # t0 = time.clock()
    gesture = check_gesture(fps)
    t1 = time.time()
    tc0 = time.clock()
    fps = 1/(t1-t0)
    print("FPS : %s" %fps)
    # print("Gesture : %s" %gesture)
    # lock.release()

    if gesture == "undefined action":

        end_time = timer()
        diff_time = end_time - start_time
        # print("Different time : %s" %diff_time) 

        if diff_time >= 1:
            state_gesture = "undefined action"
            start_time = end_time

        last_gesture = "undefined action"

        # if undefined_count == 7:                    # if found 7 undefined actions
        #     undefined_count = 0                     # reset count
        #     state_gesture = "undefined action"      # set state to undefined

        # else:
        #     undefined_count += 1                    # update count

        last_gesture = "undefined action"           # set last gesture to undefined
    
    elif last_gesture != gesture:                   # if latest gesture is not same as last gesture

        if last_gesture == "undefined action":      # if last gesture is undefined

            if state_gesture != gesture:            # check previous state before undefined if same as latest not do anything
                key_mapping(gesture)                # if not map gesture
            
        else:
            key_mapping(gesture)                # if last gesture is other gesture then map gesture

        last_gesture = gesture                  # set last gesture with latest gesture
        state_gesture = gesture                 # set state with latest gesture
        # undefined_count = 0                     # reset count

        end_time = timer()
        diff_time = end_time - start_time
        # print("Action time : %s" %diff_time)
        start_time = end_time
        
    tt1 = time.time()
    # tc1 = time.clock()
    # used_time = used_time + (tc1 - tc0)
    # tc0 = tc1
    t0 = t1
    # c = c + 1

    blob_time = time.clock()-start
    # print("blob tracking time : %s \n" %(blob_time))

    full_process_time = img_pro_time+blob_time
    print("full process time : %s \n" %(full_process_time))

    if(tt1>tt0+1):
        # print("write row")
        # percent = used_time*100/(tt1 - tt0)
        # fps_a = c / used_time
        file = open("clock time pipeline rpi.csv","a")
        file.write(str(datetime.datetime.now()) + "," + str(gesture) + "," + str(last_gesture) + "," + str(state_gesture) + "," + str(full_process_time) + "," + str(tt1 - tt0) + "\n")
        # file.write(str(datetime.datetime.now()) + "," + str(fps_a) + "," + str(percent) + "," + str(used_time) + "," + str(tt1 - tt0) + "\n")
        file.close()
        # used_time = 0
        # c = 0
        tt0 = t0

    # lock.release()
    # print("keymap time : %s \n" %(timer()-start))

    # return state

xsize,ysize = 280,210
# xsize,ysize = 640,480

if __name__ == "__main__":

    lock = Lock()

    q1 = Queue()
    q2 = Queue()

    show_page()

    p0 = Process(target=get_contours_new,args=(q1,q2,lock,))
    p1 = Process(target=blob_tracking,args=(q1,q2,lock,))

    p0.start()
    p1.start()

    p0.join()
    p1.join()


from freenect import sync_get_depth as get_depth
import numpy as np
import cv2
import math
import pygame
import time

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
    
    def set_isHand(self):
        self.isHand = True
    
    def isGrab(self):
        if self.isHand:
            contourArea = cv2.contourArea(cv2.convexHull(self.contour))
            if self.area > 0.7*contourArea :
                return True
            else:
                return False
        else:
            return False

    def isNear(self,ref):
        (x1,y1) = self.centroid
        (x2,y2) = ref.centroid
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist < 150:
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

def get_contours(xsize,ysize):
    (depth,_) = get_depth()
    depth = depth.astype(np.float32)
    depth = cv2.flip(depth, 1)
    #depth = cv2.GaussianBlur(depth, (5,5), 0)
    #depth = cv2.erode(depth, None, iterations=1)
    #depth = cv2.dilate(depth, None, iterations=1)
    min_depth = 400
    min_hand_depth = np.amin(depth)
    if min_hand_depth < min_depth:
        min_hand_depth = min_depth
    hand_depth = 100
    max_hand_depth = min_hand_depth + hand_depth
    if max_hand_depth > 700 :
        max_hand_depth = 700
    (_,BW) = cv2.threshold(depth, max_hand_depth, min_hand_depth, cv2.THRESH_BINARY_INV)
    BW = cv2.convertScaleAbs(BW)
    BW = cv2.resize(BW,(xsize,ysize))
    cs,_ = cv2.findContours(BW,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cs_f = []
    for i in range(len(cs)):
        if cv2.contourArea(cs[i]) > 2000:
            cs_f.append(cs[i])
    del depth,BW
    return cs_f

blobs = []
buffer_size = 3
blobs_buffer = [[]] * buffer_size
old_id = [[]] * buffer_size
blobs_movement = {}

def blobs_track(blob,i,n):
    global blobs
    global blobs_movement
    if blobs_buffer[n] == []:
        if n+1 < buffer_size:
            blobs_track(blob,i,n+1)
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
                        blobs_track(blob,i,n+1)
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
                    if blobs_buffer[n][j].isHand:
                        blob.set_isHand()
                    blobs_movement[new_id].append(blob.centroid)
                    blobs_movement[new_id] = blobs_movement[new_id][-20:]
                if blob.id != -1:
                    break
        if blob.id == -1:
            if n+1 < buffer_size:
                blobs_track(blob,i,n+1)
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
    for blob in blobs:
        if blob.isHand:
            id_hand.append(blob.id)
    n_hand = len(id_hand)
    if n_hand == 0:
        return "undefined action"
    elif n_hand == 1:
        n_frames = int(fps)+1
        vector = blobs_movement[id_hand[0]][-n_frames:]
        weight = {"swipe left":0,"swipe right":0}
        for i in range(len(vector)):
            if i == 0 :
                (x0,y0) = blobs_movement[id_hand[0]][0]
            else:
                (x1,y1) = blobs_movement[id_hand[0]][i]
                radian = math.atan2(y1-y0,x1-x0)
                degree = math.degrees(radian)
                dist = math.hypot(x1-x0,y1-y0)
                if dist > 20:
                    if degree>-45 and degree<45:
                        weight["swipe right"] += 1
                    elif degree>135 or degree<-135:
                        weight["swipe left"] += 1
                (x0,y0) = (x1,y1)
        ans = max(weight, key=weight.get)
        p80 = (8/10)*(n_frames-1)
        if weight[ans] > p80 :
            return ans
        else:
            return "undefined action"
    else:
        return "undefined action"

def update_old_id():
    global old_id
    for i in range(buffer_size):
        old_id[i] = []
        for j in range(len(blobs_buffer[i])):
            old_id[i].append(blobs_buffer[i][j].id)

t0 = 0

def pygame_init(xsize,ysize):
    pygame.init()
    global screen
    screen = pygame.display.set_mode((xsize,ysize),pygame.RESIZABLE)
    pygame.font.init()
    global font
    font = pygame.font.SysFont('Liberation Mono', 20)
    global t0
    t0 = time.time()

def pygame_refresh(xsize,ysize):
    screen.fill(BLACK)
    global blobs
    blobs = []
    global blobs_buffer
    global old_id
    global blobs_movement
    update_old_id()
    cs = get_contours(xsize,ysize)
    for i in range(len(cs)):
        blob = BlobAnalysis(cs[i])
        blob = blobs_track(blob,i,0)
        blobs.append(blob)
    for i in range(buffer_size):
        if i == 0:
            blobs_buffer[i] = blobs
        else:
            blobs_buffer[i] = blobs_buffer[i-1]
    for blob in blobs:
        pygame.draw.lines(screen,BLUE,False,blobs_movement[blob.id],1)
        pygame.draw.lines(screen,GREEN,True,blob.convex_hull,3)
        pygame.draw.lines(screen,YELLOW,True,blob.contour_point,3)
        pygame.draw.circle(screen,RED,blob.centroid,10)
        for tips in blob.convex_hull:
            pygame.draw.circle(screen,PURPLE,tips,5)
        if blob.isHand:
            blob_status = "ID: %d >> THIS IS HAND!!!" % (blob.id)
        else:
            blob_status = "ID: %d Hull: %d Deflect90: %d" % (blob.id,blob.approx_hull_count,blob.deflect_count_90)
        blob_status_render = font.render(blob_status, True, WHITE)
        screen.blit(blob_status_render, blob.centroid)
    global t0
    t1 = time.time()
    fps = 1/(t1 - t0)
    t0 = t1
    fps_text = "fps: %.2f" % (fps)
    fps_render = font.render(fps_text, True, WHITE)
    screen.blit(fps_render, (2,2))
    gesture_text = check_gesture(fps)
    gesture_render = font.render(gesture_text, True, WHITE)
    screen.blit(gesture_render, (2,20))
    pygame.display.set_caption('Kinect Tracking')
    #pygame.display.flip()
    return 1

xsize,ysize = 640,480
def main():
    global xsize,ysize
    pygame_init(xsize,ysize)
    #while True:
    #    pygame_refresh(xsize,ysize)

def get_input():
    global xsize,ysize
    pygame_refresh(xsize,ysize)

main()
#get_input()
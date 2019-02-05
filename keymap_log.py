# -*- coding: utf-8 -*-

import webview
import os

from pynput.keyboard import Key, Controller as keyboard_con
from pynput.mouse import Button, Controller as mouse_con
import datetime,time

import kinect_hand as input

from threading import Thread

def show_page():
    os.system("chromium-browser -no-sandbox --app=file:///home/pi/Desktop/kinect_hand_detection_and_tracking_2/src/index.html")
    #webview.create_window("It works!", url="src/index.html", width=560, height=800, fullscreen=False, background_color="#000000")

def keymap():
    keyboard = keyboard_con()
    mouse = mouse_con()
    os.system("sleep 15")
    keyboard.press(Key.f11)
    keyboard.release(Key.f11)
    fps = 0
    last_gesture = "undefined action"
    t0 = time.time()
    tt0 = t0
    tt1 = t0
    used_time = 0
    c = 0
    while True:
        tc0 = time.clock()
        input.get_input()
        gesture = input.check_gesture(fps)
        t1 = time.time()
        fps = 1/(t1-t0)
        if last_gesture != gesture:
            if gesture == "swipe up":
                #keyboard.press(Key.up)
                #keyboard.release(Key.up)
                mouse.scroll(0 , -50)
            if gesture == "swipe down":
                #keyboard.press(Key.down)
                #keyboard.release(Key.down)
                mouse.scroll(0 , 50)
            if gesture == "swipe left":
                keyboard.press(Key.right)
                keyboard.release(Key.right)
            if gesture == "swipe right":
                keyboard.press(Key.left)
                keyboard.release(Key.left)
        last_gesture = gesture
        tt1 = time.time()
        tc1 = time.clock()
        used_time = used_time + (tc1 - tc0)
        tc0 = tc1
        t0 = t1
        c = c + 1
##        if(tt1>tt0+1):
##            print "write row"
##            percent = used_time*100/(tt1 - tt0)
##            fps_a = c / used_time
##            file = open("temp.csv","a")
##            file.write(str(datetime.datetime.now()) + "," + str(fps_a) + "," + str(percent) + "," + str(used_time) + "," + str(tt1 - tt0) + "\n")
##            file.close()
##            used_time = 0
##            c = 0
##            tt0 = t0

th0 = Thread(target=show_page, args=())
th0.start()
th1 = Thread(target=keymap, args=())
th1.start()


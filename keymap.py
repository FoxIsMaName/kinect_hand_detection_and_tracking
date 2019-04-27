# -*- coding: utf-8 -*-

#import webview
import os
import webbrowser
from pynput.keyboard import Key, Controller as keyboard_con
from pynput.mouse import Button, Controller as mouse_con
import datetime,time
# import multiprocessing

import kinect_hand as input

from threading import Thread

def show_page():
    #os.system("sleep 5")
    #os.system("chromium-browser -no-sandbox --app=file:///home/pi/Desktop/kinect_hand_detection_and_tracking/src/index.html")
    webbrowser.open('file://' + os.path.realpath("/home/scarletdragon/Desktop/kinect_hand_detection_and_tracking_2/src/index.html"))    #   Open Web Application

def keymap():
    keyboard = keyboard_con()
    mouse = mouse_con()
    #os.system("sleep 15")
    #keyboard.press(Key.f11)
    #keyboard.release(Key.f11)
    fps = 0
    last_gesture = "undefined action"
    t0 = time.clock()
    while True:

        input.get_input()
        gesture = input.check_gesture(fps)
        t1 = time.clock()
        fps = 1/(t1-t0)

        if last_gesture != gesture:

            #----------------------------- Palm Hand Gesture ----------------------------

            if gesture == "swipe up":
                mouse.scroll(0 , -5)            # Scroll page up
            if gesture == "swipe down":
               mouse.scroll(0 , 5)              # Scroll page down
            if gesture == "swipe left":
                keyboard.press(Key.right)
                keyboard.release(Key.right)     # Slide to next page
            if gesture == "swipe right":
                keyboard.press(Key.left)
                keyboard.release(Key.left)      # Slide to previous page

            #----------------------------- Grab Hand Gesture ----------------------------

            if gesture == "grab down":          # use to Turn on/off IoT LED and play/pause music player
                keyboard.press('x')
                keyboard.release('x')
                # print("Grab up")
            if gesture == "grab left" :         # select previous song in music playlist
                keyboard.press('z')
                keyboard.release('z')
                # print("Grab left")
            if gesture == "grab right" :        # select next song in music playlist
                keyboard.press('c')
                keyboard.release('c')
                # print("Grab right")

        time.sleep(0.2)
        last_gesture = gesture                  # Set gesture parameter to check with the next gesture
        t0 = t1

th0 = Thread(target=show_page, args=())
th0.start()
th1 = Thread(target=keymap, args=())
th1.start()

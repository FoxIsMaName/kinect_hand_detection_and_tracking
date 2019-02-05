# -*- coding: utf-8 -*-

import webview
import os

from pynput.keyboard import Key, Controller
import time

import kinect_hand as input

from threading import Thread

def show_page():
    os.system("sleep 5")
    #os.system("chromium-browser -no-sandbox --app=file:///home/pi/Desktop/kinect_hand_detection_and_tracking/src/index.html")
    os.system("chromium-browser -no-sandbox --app=http://13.229.228.18:9000/mirror/test")
    #webview.create_window("It works!", url="src/index.html", width=560, height=800, fullscreen=False, background_color="#000000")

def keymap():
    keyboard = Controller()
    os.system("sleep 25")
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
            if gesture == "swipe up":
                keyboard.press(Key.up)
                keyboard.release(Key.up)
            if gesture == "swipe down":
                keyboard.press(Key.down)
                keyboard.release(Key.down)
            if gesture == "swipe left":
                keyboard.press(Key.right)
                keyboard.release(Key.right)
            if gesture == "swipe right":
                keyboard.press(Key.left)
                keyboard.release(Key.left)
        last_gesture = gesture
        t0 = t1

th0 = Thread(target=show_page, args=())
th0.start()
th1 = Thread(target=keymap, args=())
th1.start()


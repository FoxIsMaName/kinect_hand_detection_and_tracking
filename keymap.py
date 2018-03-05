# -*- coding: utf-8 -*-

import webview

from pynput.keyboard import Key, Controller
import time

import kinect_hand as input

from threading import Thread

def show_page():
    webview.create_window("It works!", url="home.html", width=560, height=800, fullscreen=False, background_color="#000000")

def keymap():
    keyboard = Controller()
    fps = 0
    last_gesture = "undefined action"
    while True:
        t0 = time.clock()
        input.get_input()
        gesture = input.check_gesture(fps)
        t1 = time.clock()
        fps = 1/(t1-t0)
        if last_gesture != gesture:
            if gesture == "swipe up":
                keyboard.press(Key.up)
                keyboard.release(Key.up)
            if gesture == "swipe down" and last_gesture == "undefined action" :
                keyboard.press(Key.down)
                keyboard.release(Key.down)
            if gesture == "swipe left":
                keyboard.press(Key.left)
                keyboard.release(Key.left)
            if gesture == "swipe right":
                keyboard.press(Key.right)
                keyboard.release(Key.right)
        last_gesture = gesture

th0 = Thread(target=show_page, args=())
th0.start()
th1 = Thread(target=keymap, args=())
th1.start()


# -*- coding: utf-8 -*-

import webview

from pynput.keyboard import Key, Controller
import time

import kinect_hand as input

from threading import Thread

def show_page():
    webview.create_window("It works!", url="home.html", width=560, height=760, fullscreen=False, background_color="#000000")

def keymap():
    keyboard = Controller()
    fps = 0
    t_gesture = 0.0
    while True:
        t0 = time.clock()
        input.get_input()
        gesture = input.check_gesture(fps)
        t1 = time.clock()
        fps = 1/(t1-t0)
        if t_gesture == 0:
            if gesture == "swipe up":
                t_gesture = t1 + 1
                print gesture
                keyboard.press(Key.esc)
                keyboard.release(Key.esc)
            if gesture == "swipe left":
                t_gesture = t1 + 1
                print gesture
                keyboard.press(Key.left)
                keyboard.release(Key.left)
            if gesture == "swipe right":
                t_gesture = t1 + 1
                print gesture
                keyboard.press(Key.right)
                keyboard.release(Key.right)
        elif t_gesture >= t1:
            t_gesture = 0

th0 = Thread(target=show_page, args=())
th0.start()
th1 = Thread(target=keymap, args=())
th1.start()

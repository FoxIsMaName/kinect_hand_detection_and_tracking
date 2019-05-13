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
    # os.system("chromium-browser -no-sandbox --app=file:///home/pi/Desktop/kinect_hand_detection_and_tracking_2/src/index.html")
    #os.system("chrome-browser -no-sandbox --app=http://13.229.228.18:9000/mirror/test")
    webbrowser.open('file://' + os.path.realpath("/home/scarletdragon/Desktop/kinect_hand_detection_and_tracking_2/src/index.html"))
    #webview.create_window("It works!", url="src/index.html", width=560, height=800, fullscreen=False, background_color="#000000")

def key_mapping(gesture):

    keyboard = keyboard_con()
    mouse = mouse_con()

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


def get_gesture():
    #os.system("sleep 15")
    #keyboard.press(Key.f11)
    #keyboard.release(Key.f11)
    fps = 0
    last_gesture = "undefined action"
    t0 = time.time()
    tt0 = t0
    tt1 = t0
    used_time = 0
    c = 0

    undefined_count = 0     # use to count undefined action
    state_gesture = ""      # use to save state of gesture to check

    while True:

        tc0 = time.clock()
        input.get_input()                               # get depth input and do image processing and blob tracking
        gesture = input.check_gesture(fps)              # get gesture from input data
        t1 = time.time()
        fps = 1/(t1-t0)
        print("Gesture : %s \n" %gesture)

        if gesture == "undefined action":

            if undefined_count == 7:                    # if found 7 undefined actions
                undefined_count = 0                     # reset count
                state_gesture = "undefined action"      # set state to undefined
            else:
                undefined_count += 1                    # update count

            last_gesture = "undefined action"           # set last gesture to undefined

        elif last_gesture != gesture:                   # if latest gesture is not same as last gesture

            if last_gesture == "undefined action":      # if last gesture is undefined

                if state_gesture != gesture:            # check previous state before undefined if same as latest not do anything
                    key_mapping(gesture)                # if not map gesture

                last_gesture = gesture                  # set last gesture with latest gesture
                state_gesture = gesture                 # set state with latest gesture
                undefined_count = 0                     # reset count
            else:
                key_mapping(gesture)                # if last gesture is other gesture then map gesture

            last_gesture = gesture                  # set last gesture with latest gesture
            state_gesture = gesture                 # set state with latest gesture
            undefined_count = 0                     # reset count


        tt1 = time.time()
        tc1 = time.clock()
        used_time = used_time + (tc1 - tc0)
        tc0 = tc1
        t0 = t1
        c = c + 1

        # if(tt1>tt0+1):
        #    print("write row")
        #    percent = used_time*100/(tt1 - tt0)
        #    fps_a = c / used_time
        #    file = open("keymap_prototype.csv","a")
        #    file.write(str(datetime.datetime.now()) + "," + str(fps_a) + "," + str(percent) + "," + str(used_time) + "," + str(tt1 - tt0) + "\n")
        #    file.close()
        #    used_time = 0
        #    c = 0
        #    tt0 = t0

th0 = Thread(target=show_page, args=())
th0.start()
th1 = Thread(target=get_gesture, args=())
th1.start()

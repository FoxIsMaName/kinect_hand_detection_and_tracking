# -*- coding: utf-8 -*-

import pygame
from datetime import datetime
import time
import requests
import json

import kinect_hand as input

WHITE = 255,255,255
BLACK = 0,0,0

pygame.init()
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
screen.fill(BLACK)
clock = pygame.time.Clock()
done = False

pygame.font.init()
default_font = pygame.font.SysFont('piboto', 60, True)
small_font = pygame.font.SysFont('piboto', 20, True)

def show_text(text, font, align, (x,y)):
    surface = font.render(text, True, WHITE)
    if align == 'left':
        (x,y) = (x,y)
    elif align == 'right':
        x = x - surface.get_width()
    elif align == 'center':
        x = x - surface.get_width()/2
    global screen
    screen.blit(surface,(x,y))
    return {'width':surface.get_width(), 'height':surface.get_height()}

def update_clock():
    datetime_now = datetime.now()
    year = datetime_now.year
    month = datetime_now.strftime("%B")
    day = datetime_now.day
    hour = datetime_now.hour
    minute = datetime_now.minute
    second = datetime_now.second
    clock_time_str = "%.2d:%.2d:%.2d" %(hour, minute, second)
    clock_date_str = "%.2d %s %d" %(day, month, year)
    margin = 10
    size = show_text(clock_time_str, default_font, 'right', (screen_width - margin, 0))
    y_offset = size['height']
    show_text(clock_date_str, small_font, 'right', (screen_width - margin, y_offset))

def get_location():
    url = 'http://freegeoip.net/json'
    r = requests.get(url)
    j = json.loads(r.text)
    return j

def get_forecast((lat, lon)):
    key = '8b4be84f6326687a18b252e3725e1e3a'
    url = 'https://api.darksky.net/forecast/%s/%f,%f' %(key, lat, lon)
    r = requests.get(url)
    j = json.loads(r.text)
    return j

location = get_location()
geo = (location['latitude'], location['longitude'])
weather_forecast = get_forecast(geo)
def show_forecast():
    global weather_forecast
    margin = 10
    now_temp = (weather_forecast['currently']['temperature'] - 32) / 1.8
    temp_text = "%.1f%sC" %(now_temp, unichr(176))
    size = show_text(temp_text, default_font, 'left', (margin, 0))
    y_offset = size['height']
    global location
    sum_text = weather_forecast['currently']['summary']
    #now_text = "%s, %s - %s" %(location['city'], location['country_name'], sum_text)
    now_text = "%s - %s" %(location['country_name'], sum_text)
    size = show_text(now_text, small_font, 'left', (margin, y_offset))
    y_offset += int(size['height']*1.5)
    #Ex. "Thailand - Partly Cloudy"
    
    #sum_text = weather_forecast['daily']['summary']
    #show_text(sum_text, small_font, 'left', (margin, y_offset))
    #Ex. "Light rain throughout the week, with temperatures falling to 80°F on Monday."
    
    for day in weather_forecast['daily']['data']:
        weekday_text = datetime.fromtimestamp(day['time']).strftime("%a")
        min_temp = (day['temperatureMin'] - 32) / 1.8
        max_temp = (day['temperatureMax'] - 32) / 1.8
        day_text = "%s: %.1f-%.1f%sC" %(weekday_text, min_temp, max_temp, unichr(176))
        size = show_text(day_text, small_font, 'left', (margin, y_offset))
        y_offset += size['height']

menu_active = False
menu = pygame.image.load('img/menu/menu.png')
menu_t = pygame.image.load('img/menu/menu_t.png')
menu_b = pygame.image.load('img/menu/menu_b.png')
menu_l = pygame.image.load('img/menu/menu_l.png')
menu_r = pygame.image.load('img/menu/menu_r.png')
menu_center = (screen_width-menu.get_width())/2,(screen_height-menu.get_height())/2
clock_active = True
forecast_active = True

while not done:
    fps = clock.get_fps()
    screen.fill(BLACK)
    input.get_input()
    #input.draw_debug_screen()
    if clock_active:
        update_clock()
    if forecast_active:
        show_forecast()
    gesture = input.check_gesture(fps)
    if menu_active:
        screen.blit(menu,menu_center)
        (pX,pY),grab = input.check_hover()
        if pX == 1 and pY == 0:
            screen.blit(menu_t,menu_center)
        elif pX == 1 and pY == 2:
            screen.blit(menu_b,menu_center)
            if grab:
                menu_active = False
        elif pX == 0 and pY == 1:
            screen.blit(menu_l,menu_center)
            if grab:
                forecast_active = not forecast_active
                menu_active = False
        elif pX == 2 and pY == 1:
            screen.blit(menu_r,menu_center)
            if grab:
                clock_active = not clock_active
                menu_active = False
        size = show_text("Menu", small_font, 'center', (screen_width/2, screen_height/2-185))
        size = show_text("Forecast", small_font, 'center', (screen_width/2-170, screen_height/2-15))
        size = show_text("Clock", small_font, 'center', (screen_width/2+170, screen_height/2-15))
        size = show_text("Exit", small_font, 'center', (screen_width/2, screen_height/2+155))
    else:
        if gesture == "swipe up":
            menu_active = True
    pygame.display.flip()
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True


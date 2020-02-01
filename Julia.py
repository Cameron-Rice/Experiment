import math
import sys
import os

import pandas as pd

import pygame
import pygame.gfxdraw

#constants
black = [0, 0, 0]
white = [255,255,255]

# Screen params
screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
width, height = pygame.display.get_surface().get_size()

center = (int(width/2), int(height/2))
max_dist = math.hypot(*center)

rec = False
frame = 0

# Mouse cursor properties
cur = pygame.mouse
cur.set_visible(False)

cursor_data = {
    'cursor_x': [],
    'cursor_y': [],
    'dist': [],
    'vel_x': [],
    'vel_y': [],
    'frame': [],
    #'timestamp': []
}

# for use with the get_color function, normalize the dist from 0-255
def normalize_dist(x):
    return (255)*((x)/(max_dist))

# Can change cursor color based on proximity to center
def get_color(dist):
    n = normalize_dist(dist)
    return (int(n), int((255 - n)), int(0))

# Draw middle "reference" cross
def draw_ref_cross():
    pygame.gfxdraw.hline(screen, int(width/3), width - int(width/3), int(height/2), white)
    pygame.gfxdraw.vline(screen, int(width/2), height - int(height/4), int(height/4), white)

# Draw mouse circle
def draw_mouse_circle(x, y, r, color=(255,255,255), filled=False, dist=0):
    if filled:
        pygame.gfxdraw.filled_circle(screen, x, y, r, get_color(dist))
    else:
        pygame.gfxdraw.circle(screen, x, y, r, color)

# generate the output csv with cursor frame data
def generate_output():
    df = pd.DataFrame(cursor_data)
    df.to_csv('./outputs/test.csv', index=False)
    return

# ! work in progress - replay functionality !
#Load previous mouse movement data to replay
# replay_data = pd.read_csv('test.csv')

# def replay(frame):
#     if frame < len(replay_data.index):
#         data = replay_data.iloc[frame]
#         cur.set_pos(data['cursor_x'], data['cursor_y'])

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            generate_output()  
            sys.exit()

    # Watch for mouse click to begin recording, right click to stop
    if cur.get_pressed()[0] and not rec:
        rec = True
        frame = 0
    elif cur.get_pressed()[2] and rec:
        rec = False

    # Get cursor position and relative velocity
    cur_x, cur_y = cur.get_pos()
    vel_x, vel_y = cur.get_rel()
    
    # Calculate distance from Center (ref_cross)
    dist = round(math.hypot(abs(cur_x-center[0]), abs(cur_y-center[1])), 2)

    # Record data
    if rec:
#         replay(frame)
        cursor_data['cursor_x'].append(cur_x) 
        cursor_data['cursor_y'].append(cur_y)
        cursor_data['dist'].append(dist)
        cursor_data['vel_x'].append(abs(vel_x)) 
        cursor_data['vel_y'].append(abs(vel_y))
        cursor_data['frame'].append(frame)

        frame += 1

    screen.fill(black)

    draw_ref_cross()
    draw_mouse_circle(cur_x, cur_y, 20, filled=True, dist=dist) 

    pygame.display.flip()

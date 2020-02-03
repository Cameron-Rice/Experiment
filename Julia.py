import math
import sys
import os
from os import path
from datetime import datetime

import pandas as pd

import pygame
import pygame.gfxdraw

#constants
BLACK = [0, 0, 0]
GREY = [10, 10, 10]
WHITE = [255, 255, 255]

DATA_OUTPUT = "outputs"
AUDIO_INPUT = "audio"

# Screen
screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)

width, height = pygame.display.get_surface().get_size()
center = (int(width/2), int(height/2))
max_dist = math.hypot(*center)

# Audio
pygame.mixer.init()
audio = pygame.mixer.music
audio_file = ''

# Verify audio path exists, if it does, fetch the audio file.
# Otherwise, create the directory
if path.exists(AUDIO_INPUT) and path.isdir(AUDIO_INPUT):
    for _, _, files in os.walk(AUDIO_INPUT):
        if files:
            audio_file = files[0]
            audio.load(path.join(AUDIO_INPUT, audio_file))
            audio.set_endevent(pygame.constants.USEREVENT)

        break

else:
    os.mkdir(AUDIO_INPUT)
    print(f"*** ERROR ***: Must place audio file within {AUDIO_INPUT} folder!")

# Data output
output_name = ''

if not (path.exists(DATA_OUTPUT) and path.isdir(DATA_OUTPUT)):
    os.mkdir(DATA_OUTPUT)

output_name = f"{DATA_OUTPUT}/{path.splitext(audio_file)[0] if audio_file else '!NA!'}-{datetime.now().strftime('%d-%b-%Y_%H.%M.%S')}.csv"

# Mouse cursor
cur = pygame.mouse
cur.set_visible(False)

cursor_data = {
    'cursor_x': [],
    'cursor_y': [],
    'dist': [],
    'vel_x': [],
    'vel_y': [],
    'frame': [],
    'audio_ms': []
}

#get cursor color based on proximity to center, return Tuple(R,G,B)
def get_color(dist):
    # Normalize distance value to 0 - 255 range
    normalized = (255) * ((dist) / (max_dist))
    return (int(normalized), int((255 - normalized)), int(0))

# Draw middle "reference" cross
def draw_ref_cross(size):
    pygame.gfxdraw.hline(screen, center[0] - size, center[0] + size, center[1], WHITE)
    pygame.gfxdraw.vline(screen, center[0], center[1] - size, center[1] + size, WHITE)

def draw_grid(size):
    # Get number of segements
    x_segments = width / size
    y_segments = height / size

    # Draw vertical segments, draws right then left starting from center.
    for seg in range(int(x_segments / 1.5)):
        pygame.gfxdraw.vline(screen, center[0] + int(seg * size), 0, height, GREY)
        pygame.gfxdraw.vline(screen, center[0] - int(seg * size), 0, height, GREY)

    # As above, now drawing up then down from center
    for seg in range(int(y_segments / 1.5)):
        pygame.gfxdraw.hline(screen, 0, width, center[1] + int(seg * size), GREY)
        pygame.gfxdraw.hline(screen, 0, width, center[1] - int(seg * size), GREY)


# Draw mouse circle
def draw_mouse_circle(x, y, r, color=(255, 255, 255), filled=False, dist=0):
    if filled:
        pygame.gfxdraw.filled_circle(screen, x, y, r, get_color(dist))

    else:
        pygame.gfxdraw.circle(screen, x, y, r, get_color(dist))

# generate the output csv with cursor frame data
def generate_output():
    df = pd.DataFrame(cursor_data)
    df.to_csv(output_name, index=False)
    return

rec = False
frame = 0

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            generate_output()  
            sys.exit()

        elif event.type == pygame.constants.USEREVENT:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

        elif event.type == pygame.KEYDOWN:
            if event.key == 27:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

            elif event.key == 32:
                rec = True
                frame = 0
                if audio_file:
                    audio.play()

            else:
                print(event.key)

    # Get cursor position and relative velocity
    cur_x, cur_y = cur.get_pos()
    vel_x, vel_y = cur.get_rel()

    # Calculate distance from Center (ref_cross)
    dist = round(math.hypot(abs(cur_x-center[0]), abs(cur_y-center[1])), 2)

    # Record data
    if rec:
        cursor_data['cursor_x'].append(cur_x) 
        cursor_data['cursor_y'].append(cur_y)
        cursor_data['dist'].append(dist)
        cursor_data['vel_x'].append(abs(vel_x)) 
        cursor_data['vel_y'].append(abs(vel_y))
        cursor_data['frame'].append(frame)
        cursor_data['audio_ms'].append(audio.get_pos())

        frame += 1

    # Draw to scren
    screen.fill(BLACK)

    # Lower grid size = bigger segments. ¯\_(ツ)_/¯
    draw_grid(size=80)

    draw_ref_cross(size=10)
    draw_mouse_circle(x=cur_x, y=cur_y, r=10, filled=True, dist=dist)

    # Refresh screen
    pygame.display.flip()

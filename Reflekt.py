#! /usr/bin/env python

import pygame
import random
import time
from pygame.locals import *

IMG_SIDE    = 100
MARK_SIDE   = 20
PADDING     = 10
ROWS        = 4
COLS        = 6
MOVE_SPEED  = 8     # BOX_SIDE must be divided by MOVE_SPPED exactly
SCALE_SPEED = 10    # 
BOX_SIDE    = IMG_SIDE + PADDING*2
IN_MIRROR   = False

BG_COLOR    = (0,0,0)
COLORS = {
    "GREEN"     : (161,234,100),
    "RED"       : (229,75 ,99 ),
    "ORANGE"    : (250,140,66 ),
    "PURPLE"    : (142,133,226),
    "BLUE"      : (64 ,178,223),
    "LIGHTGREEN": (237,254,235),
    }

class Box(pygame.sprite.Sprite):
    """pure color block as sprite which has two states: marked and unmarked"""
    def __init__(self, color, initial_position):
        pygame.sprite.Sprite.__init__(self)

        self.color = color
        self.image = get_surface(color)

        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position

    def mark(self, marked = True):
        self.image = get_surface(self.color, marked)

    def move(self, vector):
        self.rect = self.rect.move(vector)

class Animation():
    """basic animation unit, it will be started after it's parent is finished"""
    def __init__(self, action, box, target = None, parent = None):
        self.action = action
        self.box    = box
        self.target = target
        self.parent = parent
        self.finished  = False

    def update(self):
        if self.action == "move" :
            topleft = self.box.rect.topleft
            if not topleft == self.target:
                x_speed = MOVE_SPEED*cmp(self.target[0] - topleft[0], 0)
                y_speed = MOVE_SPEED*cmp(self.target[1] - topleft[1], 0)
                self.box.move((x_speed,y_speed))
            if self.box.rect.topleft == self.target:
                self.finished = True
        elif self.action == "renew" :
            box_side = self.box.image.get_size()[0]
            if not box_side == 0:
                self.box.image = pygame.transform.scale(self.box.image, (box_side - SCALE_SPEED, )*2)
                self.box.move((SCALE_SPEED/2, )*2)
            if self.box.image.get_size()[0] == 0:
                self.finished = True  
                new_color = self.target[0]
                self.box.image = get_surface(new_color)
                self.box.color = new_color
                new_pos = self.target[1]
                self.box.move((new_pos[0] - self.box.rect.left, new_pos[1] - self.box.rect.top))
        else:
            self.finished = True

def get_random_color():
    return random.choice(COLORS.keys())

def get_different_color(color):
    return random.choice(COLORS.keys().remove(color))

def get_surface(color, marked = False, surfaces = {}):
    key = color if not marked else color + "_MARKED"
    surface = surfaces.get(key)
    if not surface:
        surface = pygame.Surface((BOX_SIDE, BOX_SIDE))
        surface.fill(BG_COLOR)
        img = pygame.Surface((IMG_SIDE, IMG_SIDE))
        img.fill(COLORS[color])
        surface.blit(img, (PADDING, PADDING))
        if marked:
            img_mark = pygame.Surface((MARK_SIDE,MARK_SIDE))
            img_mark.fill(BG_COLOR)
            surface.blit(img_mark,((BOX_SIDE - MARK_SIDE)/2,(BOX_SIDE - MARK_SIDE)/2))
        surfaces[key] = surface
    return surface

        
def generate_boxs():
    boxs = [] 
    for y in range(0,ROWS):
        for x in range(0,COLS):
            color = get_random_color()
            b = Box(color , (BOX_SIDE*x, BOX_SIDE*y))
            boxs.append(b)
    return boxs

def generate_mirror_colors(boxs):
    for box in boxs:
        colr = box.color

def pos_to_index(pos):
    index =  pos[0]/BOX_SIDE + COLS*(pos[1]/BOX_SIDE)
    return index if index >= 0 and index < COLS*ROWS else -1

def index_to_pos(index):
    return ((index%COLS)*BOX_SIDE, (index/COLS)*BOX_SIDE)

def row_gap(you, me):
    return you/COLS - me/COLS

def col_gap(you, me):
    return you%COLS - me%COLS

def is_around(you, me):
    return abs(row_gap(you, me)) + abs(col_gap(you, me)) in (1,0)

def click_at(pos, boxs, marked_index):
    clicked_index= pos_to_index(pos)
    cmds = []
    if clicked_index == -1:
        return cmds, marked_index
    if marked_index == -1:
        boxs[clicked_index].mark(True)
        marked_index = clicked_index
    elif clicked_index == marked_index:
        boxs[clicked_index].mark(False)
        marked_index = -1
    elif is_around(clicked_index, marked_index):
        marked_box = boxs[marked_index]
        clicked_box = boxs[clicked_index]
        marked_box.mark(False)
        cmds.append("switch %s %s" % (clicked_index, marked_index))
        # cmds.append("3 1 renew %s %s" % (clicked_index, get_random_color()))
        # cmds.append("4 2 renew %s %s" % (marked_index, get_random_color()))
        # cmds.append("landslip %s %s %s %s"  % (clicked_index, get_random_color(), marked_index, get_random_color()))
        cmds.append("landslip %s %s"  % (clicked_index, get_random_color()))

        marked_index = -1
    return cmds, marked_index

def parse_command(command_str, boxs):
    commands = command_str.split(";")
    animations = []
    for command in commands:
        params = command.split()
        action = params[0]
        if action == "switch":
            f_index = int(params[1])
            t_index = int(params[2])
            animation = Animation("move", boxs[f_index])
            animation.target = index_to_pos(t_index)
            animations.append(animation)
            animation = Animation("move", boxs[t_index])
            animation.target = index_to_pos(f_index)
            animations.append(animation)
            # boxs[f_index], boxs[t_index] = boxs[t_index], boxs[f_index]
        elif action == "landslip":
            landslips = sorted(zip([int(x) for x in params[1::2]], params[2::2]), reverse=True)
            renew_parent = animations[-1]
            flag = -1
            for i, (slip_at, new_color) in enumerate(landslips):
                renew = Animation("renew", boxs[slip_at])
                renew.target = (new_color, (boxs[slip_at].rect.left, ROWS*BOX_SIDE))
                renew.parent = renew_parent 
                animations.append(renew)
                if col_gap(slip_at, flag) == 0:
                    move_parent = animations[-2]
                else:
                    move_parent = animations[-1]
                flag = slip_at

                move_animation = Animation("move", boxs[slip_at])
                move_animation.target = (boxs[slip_at].rect.left, (ROWS - 1)*BOX_SIDE)
                move_animation.parent = move_parent
                animations.append(move_animation)

                for a, b in [(i, i + COLS) for i in range(slip_at, (ROWS-1)*COLS, COLS)]:
                    move_animation = Animation("move", boxs[b])
                    move_animation.target = index_to_pos(a)
                    move_animation.parent = move_parent
                    animations.append(move_animation)
                    boxs[a], boxs[b] = boxs[b], boxs[a]

    return animations

def run_animations(animations):
    for animation in animations:
        if not animation.parent:
            animation.update()
    new_animations = []
    for animation in animations:
        if not animation.finished:
            new_animations.append(animation)
            if animation.parent and animation.parent.finished:
                animation.parent = animation.parent.parent
    return new_animations


def main():
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((BOX_SIDE * COLS, BOX_SIDE * ROWS))
    pygame.display.set_caption("Mirror Mirror")

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(BG_COLOR)

    cmds = []
    mirror_colors=[]
    animations=[]
    marked_index = -1
    boxs = generate_boxs()

    clock = pygame.time.Clock()
    while 1:
        clock.tick(60)
        if len(animations) == 0 and len(cmds) > 0:
            animations = parse_command(";".join(cmds), boxs)
            cmds = []
        if len(animations) > 0:
            animations = run_animations(animations)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == MOUSEBUTTONUP:
                if len(animations) == 0:
                    cmds, marked_index = click_at(event.pos, boxs, marked_index)
        screen.blit(background, (0,0))
        for box in boxs:
            screen.blit(box.image, box.rect)
        if IN_MIRROR:
            mirror = pygame.transform.flip(screen, False, True)
            screen.blit(background, (0,0))
            screen.blit(mirror, (0,0))
        pygame.display.flip()

if __name__ == '__main__': main()
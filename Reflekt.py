#! /usr/bin/env python

import pygame
import random
import time
from pygame.locals import *

BOX_SIDE    = 100
MARK_SIDE   = 20
PADDING     = 20
ROWS        = 4
COLS        = 6
MOVE_SPEED  = 8 # BOX_SIDE + PADDING must be divided by SPPED exactly
SCALE_SPEED = 10
IN_MIRROR   = False
BLOCK_SIDE  = BOX_SIDE + PADDING

BG_COLOR   = (0,0,0)
COLORS = {
    "GREEN"     : (161,234,100),
    "RED"       : (229,75 ,99 ),
    "ORANGE"    : (250,140,66 ),
    "PURPLE"    : (142,133,226),
    "BLUE"      : (64 ,178,223),
    "LIGHTGREEN": (237,254,235),
    }
cmds = []
boxs =[]
mirror_colors=[]
animations=[]
marked_index = -1

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
    """basic animation unit, an animation will be started only when it's parent is finished"""
    def __init__(self, action, box, target = None, parent = None):
        self.action = action
        self.box    = box
        self.target = target
        self.parent = parent
        self.finished  = False
        self.first_run = True 

    def update(self):
        if(self.action == "move"):
            topleft = self.box.rect.topleft
            if self.first_run:
                self.target = (topleft[0] + self.target[0]*BLOCK_SIDE, topleft[1] + self.target[1]*BLOCK_SIDE)
            if not topleft == self.target:
                x_speed = MOVE_SPEED*cmp(self.target[0] - topleft[0], 0)
                y_speed = MOVE_SPEED*cmp(self.target[1] - topleft[1], 0)
                self.box.move((x_speed,y_speed))
            if self.box.rect.topleft == self.target:
                self.finished = True
                global boxs
                boxs[self.target[0]/BLOCK_SIDE + COLS*(self.target[1]/BLOCK_SIDE)] = self.box
        elif(self.action == "renew"):
            box_side = self.box.image.get_size()[0]
            if not box_side == 0:
                self.box.image = pygame.transform.scale(self.box.image, (box_side - SCALE_SPEED, )*2)
                self.box.move((SCALE_SPEED/2, )*2)
            if self.box.image.get_size()[0] == 0:
                self.finished = True  
                self.box.move((-(self.box.rect.left%BLOCK_SIDE)+PADDING/2, ROWS*BLOCK_SIDE+PADDING/2-self.box.rect.top))
                self.box.image = get_surface(self.target)
                self.box.color = self.target
        else:
            self.finished = True
        self.first_run = False

def get_random_color():
    return random.choice(COLORS.keys())

def get_different_color(color):
    return random.choice(COLORS.keys().remove(color))

def get_surface(color, marked = False, surfaces = {}):
    key = color if not marked else color + "_MARKED"
    surface = surfaces.get(key)
    if not surface:
        surface = pygame.Surface((BOX_SIDE, BOX_SIDE))
        surface.fill(COLORS[color])
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
            b = Box(color , (PADDING/2 + BLOCK_SIDE*x, PADDING/2 + BLOCK_SIDE*y))
            boxs.append(b)
    return boxs

def generate_mirror_colors(boxs):
    for box in boxs:
        colr = box.color

def pos_to_index(pos):
    index =  pos[0]/BLOCK_SIDE + COLS*(pos[1]/BLOCK_SIDE)
    return index if index >= 0 and index < len(boxs) else -1

def is_around(you, me):
    if you/COLS == me/COLS and (you - me) in (-1,0,1):
        return True
    if (you - me) in (-COLS, COLS):
        return True
    return False

def get_move(start, end):
    return (start, end%COLS - start%COLS, end/COLS - start/COLS)

def click_at(pos):
    global boxs, marked_index, cmds
    clicked_index= pos_to_index(pos)
    if clicked_index == -1:
        return
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
        cmds.append("1 0 move %s %s %s" % get_move(clicked_index, marked_index))
        cmds.append("2 0 move %s %s %s" % get_move(marked_index, clicked_index))
        cmds.append("3 1 renew %s %s" % (clicked_index, get_random_color()))
        cmds.append("4 2 renew %s %s" % (marked_index, get_random_color()))
        cmds.append("5 3 landslip %s %s"  % (clicked_index, marked_index))

        marked_index = -1

def parse_command(command_str):
    commands = command_str.split(";")
    cmd_tmp = {}
    animations = []
    global boxs
    for command in commands:
        params = command.split()
        animation = Animation(params[2], boxs[int(params[3])])
        cmd_tmp[params[0]] = animation
        animation.parent = cmd_tmp.get(params[1])
        if animation.action == "move":
            animation.target = (int(params[4]), int(params[5]))
            animations.append(animation)
        elif animation.action == "renew":
            animation.target = params[4]
            animations.append(animation)
        elif animation.action == "landslip":
            landslips = sorted(zip([int(x) for x in params[3::2]], params[4::2]), reverse=True)
            parent = animation.parent
            for i, (slip_at, new_color) in enumerate(landslips):
                renew = Animation("renew", boxs[slip_at])
                renew.target = ((boxs[slip_at].rect.left, (ROWS+len(landslips)-1-i)*BLOCK_SIDE + PADDING/2), new_color)
                renew.parent = animation.parent
                animations.append(renew)
                move_animation = Animation("move", boxs[slip_at])
                for a, b in [(i, i + COLS) for i in range(slip_at, len(boxs) - COLS, COLS)]:
                    boxs[a], boxs[b] = boxs[b], boxs[a]
                    move_animation = Animation("move", box)
                    move_animation.target = (0, -1)
                    move_animation.parent = parent
                    animations.append(move_animation)
                if len(landslips) == 2 and landslips[0] - landslips[1] == COLS:
                    parent = animations[-1]
            cmd_tmp[params[0]] = animations[-1]

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
    return new_animation    s


def main():
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode([(BOX_SIDE + PADDING) * COLS,(BOX_SIDE + PADDING) * ROWS])
    pygame.display.set_caption("Mirror Mirror")

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(BG_COLOR)

    global boxs, animations,cmds
    boxs = generate_boxs()

    clock = pygame.time.Clock()
    while 1:
        clock.tick(60)
        if len(animations) == 0 and len(cmds) > 0:
            animations = parse_command(";".join(cmds))
            cmds = []
        if len(animations) > 0:
            animations = run_animations(animations)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == MOUSEBUTTONUP:
                if len(animations) == 0:
                    click_at(event.pos)
        screen.blit(background, (0,0))
        for box in boxs:
            # box.draw(screen)
            screen.blit(box.image, box.rect)
        if IN_MIRROR:
            mirror = pygame.transform.flip(screen, False, True)
            screen.blit(background, (0,0))
            screen.blit(mirror, (0,0))
        pygame.display.flip()

if __name__ == '__main__': main()
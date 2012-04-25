import pygame
import random
from pygame.locals import *

BOX_SIDE    = 100
MARK_SIDE   = 20
PADDING     = 20
ROWS        = 4
COLS        = 6
MOVE_SPEED  = 8 # BOX_SIDE + PADDING must be divided by SPPED exactly
SCALE_SPEED = 10

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

boxs =[]
mirror_colors=[]
animations=[]
marked_box = -1

class Box(pygame.sprite.Sprite):
    """pure color block as sprite which has two states: marked and unmarked"""
    def __init__(self, color, initial_position):
        pygame.sprite.Sprite.__init__(self)

        self.img_normal = pygame.Surface((BOX_SIDE,BOX_SIDE))
        self.img_normal.fill(COLORS[color])

        self.img_mark = pygame.Surface((MARK_SIDE,MARK_SIDE))
        self.img_mark.fill(BG_COLOR)
        self.img_marked= pygame.Surface((BOX_SIDE,BOX_SIDE))
        self.img_marked.fill(COLORS[color])
        self.img_marked.blit(self.img_mark,((BOX_SIDE - MARK_SIDE)/2,(BOX_SIDE - MARK_SIDE)/2))

        self.image = self.img_normal
        self.color = color

        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position

    def clicked(self):
        if self.image == self.img_normal:
            self.image = self.img_marked
        else:
            self.image = self.img_normal

class Animation():
    """basic animation unit, an animation will be started only when it's parent is finished"""
    def __init__(self, action, box, target, state = None, parent = None):
        self.action = action
        self.box    = box
        self.target = target
        self.parent = parent
        self.state  = state
        self.finished = False

    def update(self):
        if(self.action == "move"):
            topleft = self.box.rect.topleft
            if not topleft == self.target:
                x_speed = MOVE_SPEED*cmp(self.target[0] - topleft[0], 0)
                y_speed = MOVE_SPEED*cmp(self.target[1] - topleft[1], 0)
                self.box.rect = self.box.rect.move((x_speed,y_speed))
            else:
                self.finished = True
        elif(self.action == "zoom_out"):
            box_side = self.box.image.get_size()[0]
            if not box_side == self.target:
                self.box.image = pygame.transform.scale(self.box.image, (box_side - SCALE_SPEED, )*2)
                self.box.rect = self.box.rect.move((SCALE_SPEED/2, )*2)
            else:
                self.finished = True
                self.box.image = self.state
                box_side = self.box.image.get_size()[0]
                self.box.rect = self.box.rect.move(((self.target - box_side)/2, )*2)
        
def generate_boxs():
    boxs = [] 
    color_keys = COLORS.keys()
    for y in range(0,ROWS):
        for x in range(0,COLS):
            r = random.randint(0,len(color_keys)-1)
            b = Box(color_keys[r], (PADDING/2 + BLOCK_SIDE*x, PADDING/2 + BLOCK_SIDE*y))
            boxs.append(b)
    return boxs

def generate_mirror_colors(boxs):
    for box in boxs:
        colr = box.color

def pos_to_index(pos):
    index =  pos[0]/BLOCK_SIDE + COLS*(pos[1]/BLOCK_SIDE)
    return index if index >= 0 and index < len(boxs) else -1

def switch_box(indexA, indexB):
    global boxs, animations
    boxs[indexA], boxs[indexB] = boxs[indexB], boxs[indexA]
    animations.append(Animation("move", boxs[indexA], boxs[indexB].rect.topleft))
    animations.append(Animation("move", boxs[indexB], boxs[indexA].rect.topleft))

def is_around(you, me):
    if you/COLS == me/COLS and (you - me) in (-1,0,1):
        return True
    if (you - me) in (-COLS, COLS):
        return True
    return False

def click_at(pos):
    global boxs, marked_box, animations
    if len(animations) > 0:
        return
    clicked_box = pos_to_index(pos)
    if clicked_box == -1:
        return
    if marked_box == -1:
        boxs[clicked_box].clicked()
        marked_box = clicked_box
    elif clicked_box == marked_box:
        boxs[clicked_box].clicked()
        marked_box = -1
    elif is_around(clicked_box, marked_box):
        boxs[marked_box].clicked()
        switch_box(clicked_box, marked_box)
        marked_box = -1
        # selected_zoom_out = Animation("zoom_out", clicked_box, 0, clicked_box.image, selected_move)

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
    screen = pygame.display.set_mode([(BOX_SIDE + PADDING) * COLS,(BOX_SIDE + PADDING) * ROWS])
    pygame.display.set_caption("Mirror Mirror")

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(BG_COLOR)
    #screen.blit(background, [0,0])
    # pygame.display.flip()

    global boxs, animations
    boxs = generate_boxs()

    pygame.display.update()
    clock = pygame.time.Clock()
    while 1:
        clock.tick(60)
        animations = run_animations(animations)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == MOUSEBUTTONUP:
                click_at(event.pos)
        screen.blit(background, [0,0])
        for box in boxs:
            # box.draw(screen)
            screen.blit(box.image, box.rect)
        pygame.display.update()
        # pygame.display.flip()

if __name__ == '__main__': main()
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
marked_box_index = -1
surfaces={}

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
    def __init__(self, action, box, target = None, state = None, parent = None):
        self.action = action
        self.box    = box
        self.target = target
        self.parent = parent
        self.state  = state
        self.finished  = False

    def update(self):
        if(self.action == "change_color"):
            self.box.image = self.target
            self.finished = True
        elif(self.action == "jump"):
            self.box.move((self.target[0] - self.box.rect.left, self.target[1] - self.box.rect.top))
            self.finished = True
        elif(self.action == "move"):
            topleft = self.box.rect.topleft
            if not topleft == self.target:
                x_speed = MOVE_SPEED*cmp(self.target[0] - topleft[0], 0)
                y_speed = MOVE_SPEED*cmp(self.target[1] - topleft[1], 0)
                self.box.move((x_speed,y_speed))
            else:
                global boxs
                boxs[self.target[0]/BLOCK_SIDE + COLS*(self.target[1]/BLOCK_SIDE)] = self.box
                self.finished = True
        elif(self.action == "zoom_out"):
            box_side = self.box.image.get_size()[0]
            if not box_side == self.target:
                self.box.image = pygame.transform.scale(self.box.image, (box_side - SCALE_SPEED, )*2)
                self.box.move((SCALE_SPEED/2, )*2)
            else:
                self.finished = True
                self.box.move((self.state[0] - self.box.rect.left, self.state[1] - self.box.rect.top))
        else:
            self.finished = True

def get_random_color():
    return  random.choice(COLORS.keys())

def get_different_color(color):
    while True:
        new_color = get_random_color()
        if new_color != color:
            return new_color

def get_surface(color, marked = False):
    global surfaces
    key = color if not marked else color + "_MARKED"
    surface = surfaces.get(key)
    if surface:
        return surface
    else:
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

def click_at(pos):
    global boxs, marked_box_index, cmds
    clicked_box_index = pos_to_index(pos)
    if clicked_box_index == -1:
        return
    if marked_box_index == -1:
        boxs[clicked_box_index].mark(True)
        marked_box_index = clicked_box_index
    elif clicked_box_index == marked_box_index:
        boxs[clicked_box_index].mark(False)
        marked_box_index = -1
    elif is_around(clicked_box_index, marked_box_index):
        marked_box = boxs[marked_box_index]
        clicked_box = boxs[clicked_box_index]
        marked_box.mark(False)
        cmds.append("move %s %s" % (clicked_box_index, marked_box_index))
        cmds.append("move_and_disappear %s %s" % (marked_box_index, clicked_box_index))
        # cmds.append("3 1 zoom_out %s %s" % (clicked_box_index, 0))
        # cmds.append("4 2 zoom_out %s %s" % (marked_box_index, 0))
        marked_box_index = -1
        # selected_zoom_out = Animation("zoom_out", clicked_box, 0, clicked_box.image, selected_move)

def parse_command(command_str):
    commands = command_str.split(";")
    cmd_tmp = {}
    animations = []
    for command in commands:
        params = command.split()
        animation = Animation(params[2], boxs[int(params[3])])
        cmd_tmp[params[0]] = animation
        animations.append(animation)
        animation.parent = cmd_tmp.get(params[1])
        if animation.action == "move":
        animation = Animation(params[2], boxs[int(params[3])])
            target_box = boxs[int(params[4])]
            animation.target = target_box.rect.topleft
        elif animation.action == "zoom_out":
            animation.target = int(params[4])
            animation.state = animation.box.rect.topleft
        elif animation.action == "jump":
            animation.target = (int(params[4]), int(params[5]))
        elif animation.action == "change_color":
            animation.target = params[4]
        elif animation.action == "landslip":
            if len(params) == 5:
                box = boxs[int(params[3])]
                zoom_animation = Animation("zoom_out", box,)

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
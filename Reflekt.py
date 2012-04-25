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
animations=[]
marked_box = None

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
    def __init__(self, action, box, target, parent = None, state = None):
        self.action = action
        self.box    = box
        self.target = target
        self.parent = parent
        self.state  = state

    def update(self):
        finished = True
        if(self.action == "move"):
            topleft = self.box.rect.topleft
            if not topleft == self.target:
                finished = False
                x_speed = MOVE_SPEED*cmp(self.target[0] - topleft[0], 0)
                y_speed = MOVE_SPEED*cmp(self.target[1] - topleft[1], 0)
                self.box.rect = self.box.rect.move((x_speed,y_speed))
        elif(animation[1] == "zoom_out"):
            box_side = self.box.image.get_size()[0]
            if not box_side == self.target:
                finished = False
                self.box.image = pygame.transform.scale(self.box.image, (box_side - SCALE_SPEED, )*2)
                self.box.rect = self.box.rect.move((SCALE_SPEED/2, )*2)
            else:
                self.box.image = self.state
                box_side = self.box.image.get_size()[0]
                self.box.rect = self.box.rect.move(((self.target - box_side)/2, )*2)
        return finished
        
def generate_boxs():
    boxs = [] 
    color_keys = COLORS.keys()
    for y in range(0,ROWS):
        for x in range(0,COLS):
            r = random.randint(0,len(color_keys)-1)
            b = Box(color_keys[r], (PADDING/2 + BLOCK_SIDE*x, PADDING/2 + BLOCK_SIDE*y))
            boxs.append(b)
    return boxs

def find_box(pos):
    for box in boxs:
        topleft = box.rect.topleft
        if pos[0] - (topleft[0] - PADDING/2) < 0:   
            continue
        if pos[0] - (topleft[0] - PADDING/2) >= BLOCK_SIDE:
            continue
        if pos[1] - (topleft[1] - PADDING/2) < 0:
            continue
        if pos[1] - (topleft[1] - PADDING/2) >= BLOCK_SIDE:
            continue
        return box
    return None

def is_around(you, me):
    p_you = you.rect.topleft
    p_me  = me.rect.topleft
    if abs(p_you[0] - p_me[0]) in (0, BOX_SIDE + PADDING) and p_you[1] == p_me[1]:
        return True
    elif abs(p_you[1]-p_me[1]) in (0, BOX_SIDE + PADDING) and p_you[0] == p_me[0]:
        return True
    return False

def click_at(pos):
    global boxs, marked_box, animations
    if len(animations) > 0:
        return
    clicked_box = find_box(pos)
    if not clicked_box:
        return
    if marked_box is None:
        clicked_box.clicked()
        marked_box = clicked_box
    elif clicked_box == marked_box:
        clicked_box.clicked()
        marked_box = None
    elif is_around(clicked_box, marked_box):
        marked_box.clicked()
        selected_move     = [None, "move", clicked_box, marked_box.rect.topleft]
        selected_zoom_out = [selected_move, "zoom_out", clicked_box, (0,0), clicked_box.image]
        marked_move       = [None, "move", marked_box, clicked_box.rect.topleft]
        animations.extend([selected_move, selected_zoom_out, marked_move])
        marked_box = None



def run_animations():
    global animations
    finished = []
    for animation in animations:
        if not animation[0]:
            if not update_animation(animation):
                finished.append(animation)
    new_animations = []
    for animation in animations:
        if not animation in finished:
            if animation[0] in finished:
                animation[0] = animation[0][0]
            new_animations.append(animation)
    animations = new_animations


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

    global boxs
    boxs = generate_boxs()

    pygame.display.update()
    clock = pygame.time.Clock()
    while 1:
        clock.tick(60)
        run_animations()
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
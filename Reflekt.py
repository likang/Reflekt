import pygame
import random
from pygame.locals import *

BOX_WIDTH       = 100
BOX_HEIGHT      = 100
MARK_WIDTH      = 20
MARK_HEIGHT     = 20
ROWS_PADDING    = 20
COLS_PADDING    = 20
ROWS            = 4
COLS            = 6
SPEED           = 8 # BOX_WIDTH + COLS_PADDING and BOX_HEIGHT + ROWS_PADDING must can be divided by SPPED exactly

BG_COLOR   = [0,0,0]
COLORS = {
	"GREEN"     : [161,234,100],
	"RED"       : [229,75 ,99 ],
	"ORANGE"    : [250,140,66 ],
	"PURPLE"    : [142,133,226],
	"BLUE"      : [64 ,178,223],
	"LIGHTGREEN": [237,254,235],
	}

boxs =[]
animations=[]
marked_box = None

class Box(pygame.sprite.Sprite):
    def __init__(self, color, initial_position):
        pygame.sprite.Sprite.__init__(self)

        self.img_normal = pygame.Surface([BOX_WIDTH,BOX_HEIGHT])
        self.img_normal.fill(color)

        self.img_mark = pygame.Surface([MARK_WIDTH,MARK_HEIGHT])
        self.img_mark.fill(BG_COLOR)
        self.img_marked= pygame.Surface([BOX_WIDTH,BOX_HEIGHT])
        self.img_marked.fill(color)
        self.img_marked.blit(self.img_mark,[(BOX_WIDTH - MARK_WIDTH)/2,(BOX_HEIGHT - MARK_HEIGHT)/2])

        self.image = self.img_normal
        self.color = color

        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position
    def selected(self):
    	if self.image == self.img_normal:
    		self.image = self.img_marked
    	else:
    		self.image = self.img_normal

def generate_boxs():
	boxs = [] 
	color_keys = COLORS.keys()
	for y in range(0,ROWS):
		for x in range(0,COLS):
			r = random.randint(0,len(color_keys)-1)
			b = Box(COLORS[color_keys[r]], [COLS_PADDING/2 + (BOX_WIDTH + COLS_PADDING)*x,
				ROWS_PADDING/2 + (BOX_HEIGHT + ROWS_PADDING)*y])
			boxs.append(b)
	return boxs

def find_box(pos):
	global boxs
	for box in boxs:
		topleft = box.rect.topleft
		if pos[0] - (topleft[0] - COLS_PADDING/2) < 0:	
			continue
		if pos[0] - (topleft[0] - COLS_PADDING/2) >= BOX_WIDTH + COLS_PADDING:
			continue
		if pos[1] - (topleft[1] - ROWS_PADDING/2) < 0:
			continue
		if pos[1] - (topleft[1] - ROWS_PADDING/2) >= BOX_HEIGHT + ROWS_PADDING:
			continue
		return box
	return None

def is_around(you, me):
	p_you = you.rect.topleft
	p_me  = me.rect.topleft

	if abs(p_you[0] - p_me[0]) in (0, BOX_WIDTH + COLS_PADDING) and p_you[1] == p_me[1]:
		return True
	elif abs(p_you[1]-p_me[1]) in (0, BOX_HEIGHT + ROWS_PADDING) and p_you[0] == p_me[0]:
		return True
	return False

def click_at(pos):
	global boxs, marked_box, animations
	if len(animations) > 0:
		return

	selected_box = find_box(pos)
	if not selected_box:
		return

	if marked_box is None:
		selected_box.selected()
		marked_box = selected_box
	elif selected_box == marked_box:
		selected_box.selected()
		marked_box = None
	elif is_around(selected_box, marked_box):
		marked_box.selected()
		animations.append(("move", selected_box, marked_box.rect.topleft))
		animations.append(("move", marked_box, selected_box.rect.topleft))
		marked_box = None

def run_animations():
	global animations
	tmp = []
	for animation in animations:
		if type(animation) is list:
			pass
		else:
			if(animation[0] == "move"):
				p_from = animation[1].rect.topleft
				p_to = animation[2]
				if not p_from == p_to:
					x_speed = 0 if p_from[0] == p_to[0] else SPEED*(p_to[0] - p_from[0])/abs(p_to[0] - p_from[0])
					y_speed = 0 if p_from[1] == p_to[1] else SPEED*(p_to[1] - p_from[1])/abs(p_to[1] - p_from[1])
					animation[1].rect = animation[1].rect.move((x_speed,y_speed))
					tmp.append(animation)
	animations = tmp


def main():
	# Initialise screen
	pygame.init()
	screen = pygame.display.set_mode([(BOX_WIDTH + COLS_PADDING) * COLS,(BOX_HEIGHT + ROWS_PADDING) * ROWS])
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
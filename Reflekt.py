import pygame
import random
from pygame.locals import *

BOX_WIDTH       = 100
BOX_HEIGHT      = 100
MARK_WIDTH      = 20
MARK_HEIGHT     = 60
ROWS_PADDING    = 20
COLS_PADDING    = 20
ROWS            = 4
COLS            = 6

BG_COLOR   = [0,0,0]
COLORS = {
	"GREEN" : [161,234,100],
	"RED"   : [229,75 ,99 ],
	"ORANGE": [250,140,66 ],
	"PURPLE": [142,133,226],
	"BLUE"  : [64 ,178,223]}

class Box(pygame.sprite.Sprite):
    def __init__(self, color, initial_position):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([BOX_WIDTH,BOX_HEIGHT])
        self.image.fill(color)

        self.mark = pygame.Surface([MARK_WIDTH,MARK_HEIGHT])
        self.mark.fill(BG_COLOR)
        self.image.blit(self.mark,[(BOX_WIDTH - MARK_WIDTH)/2,(BOX_HEIGHT - MARK_HEIGHT)/2])

        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position

def main():
	pygame.init()
	screen = pygame.display.set_mode([(BOX_WIDTH + COLS_PADDING) * COLS,(BOX_HEIGHT + ROWS_PADDING) * ROWS])
	pygame.display.set_caption("Mirror Mirror")

	color_keys = COLORS.keys()
	for x in range(0,COLS):
		for y in range(0,COLS):
			r = random.randint(0,len(color_keys)-1)
			b = Box(COLORS[color_keys[r]], [COLS_PADDING/2 + (BOX_WIDTH + COLS_PADDING)*x,
				ROWS_PADDING/2 + (BOX_HEIGHT + ROWS_PADDING)*y])
			screen.blit(b.image, b.rect)

	pygame.display.update()
	clock = pygame.time.Clock()
	while 1:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == QUIT:
				return

		pygame.time.delay(10)

if __name__ == '__main__': main()
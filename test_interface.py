import pygame
import kinect_hand as input
import time

class Item:
    def __init__(self,x,y,sx,sy):
        self.x = x
        self.y = y
        self.sx = sx
        self.sy = sy
        self.isGrabBy = []
    def draw(self):
        pygame.draw.rect(screen, WHITE, pygame.Rect(self.x, self.y, self.sx, self.sy))
    def checkGrab(self,mx,my,mid):
        if self.x + self.sx >= mx >= self.x and self.y + self.sy >= my >= self.y:
            pos = mx,my
            grab_pos = mx - self.x, my - self.y
            exist = False
            for grab in self.isGrabBy:
                if grab[0] == mid:
                    exist = True
                    grab[2] = pos
                    break
            if exist == False:
                self.isGrabBy.append([mid,grab_pos,pos])
            return True
        else:
            return False
    def resetGrab(self):
        self.isGrabBy = []
    def action(self):
        if len(self.isGrabBy) == 1:
            self.follow()
    def follow(self):
        mid = self.isGrabBy[0][0]
        dx,dy = self.isGrabBy[0][1]
        mx,my = self.isGrabBy[0][2]
        self.x = mx - dx
        self.y = my - dy

pygame.init()
screen = pygame.display.set_mode((640, 480))
done = False
clock = pygame.time.Clock()
x,y = 100,100
sx,sy = 100,100
WHITE = 255,255,255
BLACK = 0,0,0
box = Item(x,y,sx,sy)
while not done:
    input.get_input()
    #screen.fill(BLACK)
    grabed = False
    for blob in input.blobs:
        if blob.isGrab():
            mx,my = blob.centroid
            mid = blob.id
            if box.checkGrab(mx,my,mid):
                grabed = True
    if not(grabed):
        box.resetGrab()
    box.action()
    box.draw()
    pygame.display.flip()
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            


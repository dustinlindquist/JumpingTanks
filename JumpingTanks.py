import sys
import os
import pygame
import math
import random
(width, height) = (1920, 940)
gravity=.015
gravityVector = (math.pi,gravity)#vector that represents gravity, pi is down in this system
drag = .998 #speed is degreased by this percentage over time
elasticity = .95 #amount of energy lost when particles hit each other (due to heat)
roadFriction =.99 #percentage of speed lost while on road surface
sandFriction=.95 #perfectage of speed lost while on sand surface
iceFriction=1 #percentage of speed lost while on ice surface
speed=.04 #amount of speed
lifespan=200 #how long the particles last


def addVectors((angle1, length1), (angle2, length2)):
	#Takes in 2 vectors as input and returns the resultant vector
	x=math.sin(angle1) * length1 + math.sin(angle2) * length2#gets the x length of the resultant vector
	y=math.cos(angle1)* length1 + math.cos(angle2) * length2#gets the y length of the resultant vector
	angle = .5 * math.pi - math.atan2(y,x) #gets the the angle of the resultant vector
	length = math.hypot(x,y) #gets the length of the resultant vector
	return (angle, length) #returns the resultant vector
	
def collide(particle1, particle2):
	#Takes in 2 particles and changes each of their vectors based on their starting vectors
	dx = particle1.x-particle2.x#Get the x distance between 2 particles
	dy = particle1.y-particle2.y#Get the y distance between 2 particles
	distance = math.hypot(dx,dy)#Get the total distance between 2 particles
	if distance < particle1.size + particle2.size:
		#If the distance between particles is less than their combined size then they are colliding and must react with each other
		tangent = math.atan2(dy,dx)
		angle = .5*math.pi+tangent
		angle1 = 2*tangent - particle1.angle#particle1 new angle
		angle2 = 2*tangent - particle2.angle#particle2 new angle
		speed1 = particle2.speed*elasticity#particle1 new speed
		speed2 = particle1.speed*elasticity#particle2 new speed
		
		(particle1.angle,particle1.speed)=(angle1,speed1)#Set speed and angle for particle1
		(particle2.angle,particle2.speed)=(angle2,speed2)#Set speed and angle for particle2
		
		#particle1.speed*=elasticity#loss of energy due to heat
		#particle2.speed*=elasticity#loss of energy due to heat
		#Fix Sticky Problem: move both particles a very small amount so that they do not get stuck in a collision loop
		particle1.x+=math.sin(angle)
		particle1.y-=math.cos(angle)
		particle2.x-=math.sin(angle)
		particle2.y+=math.cos(angle)

class Tank:
	def __init__(self,(x,y),size):
		self.image = pygame.image.load("tank.gif")
		self.x=x#x location
		self.y=y#y location
		self.xspeed=0
		self.yspeed=0
		self.rect = (self.x,self.y,25,25)#rect object that represent the tank sprite
		self.size=size
		
	def display(self):
		#draws the tank sprite to the screen
		screen.blit(self.image, self.rect)
		
	def move(self):
		#Moves the tank sprite based on its xspeed,yspeed and gravity
		self.yspeed-=.05#gravity
		self.x+=self.xspeed
		self.y-=self.yspeed
		self.rect=(self.x,self.y)
		
	def friction(self):
		#changes the x speed of the tank based on which part of the map it is located
		if self.y==850.05:
			if self.x<800: #road
				self.xspeed*=roadFriction
			elif self.x<1300 and self.x>800: #sand
				self.xspeed*=sandFriction
			elif self.x>1300 and self.x<1920: #ice
				self.xspeed*=iceFriction

	def bounce(self):
		#handles the tanks reaction to going past different bounds
		if self.x > width - self.size:#if the tank sprite goes past the right side reset it back to the left
			self.x = 0
		elif self.x < 0:
			self.x=width-self.size #if the tank sprite goes past the left side reset it back to the right
		if self.y > height-90: #if the tank sprite goes beyond a certain point it sets the yspeed to 0 and its y postion to the correct position. This prevents falling forever and from bouncing
			self.yspeed=0 
			self.y=850

	def jump(self):
		#Sets the yspeed up to a set ammount 
		self.yspeed+=3.5
	
class Particle:
	def __init__(self, (x, y), size,angle):
		self.x = x #x location
		self.y = y #y location
		self.size = size
		self.color = (255, 0, 0)
		self.thickness = 0
		self.speed=8
		self.angle=angle
		self.life=0

	def display(self):
		#draw the particle to the screen
		pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size, self.thickness)
	
	def isDead(self):
		#if the particle's timer reaches its limit then return true
		if self.life>lifespan:
			return True
		return False
		
	def move(self):
		(self.angle,self.speed) = addVectors((self.angle, self.speed),gravityVector) #change the speed and angle of particles based on gravity
		self.speed*=drag #lower the speed due to air resistance
		self.x+=math.sin(self.angle)*self.speed #update particle location based on speed and location
		self.y-=math.cos(self.angle)*self.speed #update particle location based on speed and location
	
	def bounce(self):
		#Bounce the particle off the walls based on their speed and angle, loss of energy due to heat is factored in
		if self.x > width - self.size:
			self.x = 2*(width - self.size) - self.x
			self.angle = -self.angle
			self.speed *= elasticity
		elif self.x<self.size:
			self.x = 2*self.size - self.x
			self.angle = - self.angle
			self.speed *= elasticity
		if self.y > height - self.size:
			self.y = 2*(height - self.size) - self.y
			self.angle = math.pi - self.angle
			self.speed *= elasticity
		elif self.y<self.size:
			self.y= 2*self.size - self.y
			self.angle = math.pi - self.angle
			self.speed *= elasticity
		
	

screen = pygame.display.set_mode((width, height))

numOfParticles=0
particles = []
shootTimer=0
jumpTimer=0
jumps=0
tank=Tank((25,height-50),80)#((start x location, start y location), size)
background = pygame.image.load("backdropLogo.gif")
running=True
while running:
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			running=False
	screen.blit(background,(0,0))#Draw the background image to the screen
	keys_pressed = pygame.key.get_pressed()
	if shootTimer<=0:
		#Shoot a particle based on the current mouse position
		if pygame.mouse.get_pressed()[0]==1:
			numOfParticles+=1
			dy=pygame.mouse.get_pos()[1]-tank.y
			dx=pygame.mouse.get_pos()[0]-tank.x
			angle=math.atan2(dy,dx)+ 0.5*math.pi
			particle = Particle((tank.x+13, tank.y), 15,angle)
			particles.append(particle)
			shootTimer=5
	
	if tank.y==850:#Only allow tank to accelerate X speed when grounded
		if keys_pressed[pygame.K_d]:
			tank.xspeed+=speed
		if keys_pressed[pygame.K_a]:
			tank.xspeed-=speed
	
	if jumpTimer<=0 < 2:
		if keys_pressed[pygame.K_w]:
			tank.jump()
			jumps+=1
			jumpTimer=7;

	for i, particle in enumerate(particles):
		particle.life+=.1
		if particle.isDead():
			particles.remove(particle)
		particle.move()
		particle.bounce()
		for particle2 in particles[i+1:]:
			collide(particle,particle2)
		particle.display()
	tank.move()
	tank.friction()
	tank.bounce()
	tank.display()
	pygame.display.flip()
	jumpTimer-=.05
	shootTimer-=.05

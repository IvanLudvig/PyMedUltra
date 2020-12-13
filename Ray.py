import json
import math
import numpy as np
from Vector2 import Vector2
from Obstacle import Obstacle
class Ray:
	def __init__(self,pos:Vector2=Vector2(),velocity:Vector2=Vector2(),material=-1,intensity=1.0,
		nextEncounter=math.inf,obstacle_number = 0,vertice_number =0,left=None,
		right=None,invalid=0,virtual_neighbors_left=np.array([]),virtual_neighbors_right=np.array([])):
		conf = 'res/config.json'
		with open(conf) as jf:
			configuration = json.load(jf)
			self.VISIBILITY_THRESHOLD = configuration["Constants"]["VISIBILITY_THRESHOLD"]
			self.SENSORS = configuration["Constants"]["SENSORS"]
			self.X = configuration["Constants"]["X"]
			self.Y = configuration["Constants"]["Y"]
		self.pos = Vector2()
		self.velocity = Vector2()
		self.material = material
		self.intensity = intensity
		self.nextEncounter = nextEncounter
		self.obstacle_number=obstacle_number
		self.vertice_number = vertice_number
		self.left = left
		self.right = right
		self.invalid=invalid
		self.virtual_neighbors_left = virtual_neighbors_left
		self.virtual_neighbors_right = virtual_neighbors_right

	def getPos(self)->Vector2:
		return self.pos
	
	def getVelocity(self):
		return self.velocity

	def getMaterial(self):
		return self.material

	def getIntensity(self):
		return self.intensity
	
	def getNextEncounter(self):
		return self.nextEncounter
	
	def getObstacleNumber(self):
		return self.obstacle_number

	def getVerticeNumber(self):
		return self.vertice_number
	
	def getLeft(self):
		return self.left
	
	def getRight(self):
		return self.right
	
	def getVirtualLeft(self):
		return self.virtual_neighbors_left

	def getVirtualRight(self):
		return self.virtual_neighbors_right
	
	def getInvalid(self):
		return self.invalid
	
	def setPos(self, pos):
		self.pos = pos
	
	def setVelocity(self, velocity):
		self.velocity = velocity
	
	def setMaterial(self, material):
		self.material = material
	
	def setIntensity(self, intensity):
		self.intensity = intensity
	
	def setNextEncounter(self, nextEncounter):
		self.nextEncounter=nextEncounter
	
	def setObstacleNumber(self, obstacle_number):
		self.obstacle_number = obstacle_number
	
	def setVerticeNumber(self, vertice_number):
		self.vertice_number = vertice_number
	
	def setLeft(self, left):
		self.left = left

	def setRight(self, right):
		self.right = right
	
	def setVirtualLeft(self, virtual_neighbors_left):
		self.virtual_neighbors_left=virtual_neighbors_left
	
	def setVirtualRight(self, virtual_neighbors_right):
		self.virtual_neighbors_right = virtual_neighbors_right

	def setInvalid(self, invalid):
		self.invalid = invalid
	
	def getPosAfterStep(self, step:float)->Vector2:
		return Vector2(self.pos.getX() + self.velocity.getX() * step, self.pos.getY() + self.velocity.getY() * step)

	def getTime(self, dist, relativeSpeed)->float:
		if (self.material >= 0):
			return math.fabs(dist / relativeSpeed)
		else:
			return math.fabs(dist)
	
	def update(self, timeStep, relativeSpeed):
		self.pos.setX(self.pos.getX() + self.velocity.getX() * timeStep * (relativeSpeed if self.material >= 0 else 1.0))
		self.pos.setY(self.pos.getY() + self.velocity.getY() * timeStep * (relativeSpeed if self.material >= 0 else 1.0))
		if ((self.nextEncounter < -0.5) or (self.nextEncounter == math.inf)):
			return
		self.nextEncounter  -= timeStep
		return

	def getReflected(self, obstacle: Obstacle):
		i = self.intensity
		vel = Vector2.getReflected(self, A = obstacle.getPos(self.vertice_number), B = obstacle.getPos(self.vertice_number + 1),
		velocity = self.velocity, relativeSpeed=obstacle.getCRel(), intensity=i)
		return Ray(Vector2(self.pos.getX() - (1.00015 * self.velocity.getX()), 
		self.pos.getY() - (1.00015 * self.velocity.getY())),vel,i)

	def getRefracted(self, obstacle: Obstacle)->Ray:
		i = self.intensity
		vel = Vector2.getRefracted(self, A = obstacle.getPos(self.vertice_number), B = obstacle.getPos(self.vertice_number + 1),
		velocity = self.velocity, relativeSpeed=obstacle.getCRel(), intensity=i)
		return Ray(Vector2(self.pos.getX() + (1.00015 * self.velocity.getX()), 
		self.pos.getY() + (1.00015 * self.velocity.getY())),vel,i)

	def addLeftVirtualNeighbor(self, neighbor:Ray):
		self.setVirtualLeft(np.concatenate((self.getVirtualLeft(), neighbor)))

	def addRightVirtualNeighbor(self, neighbor:Ray):
		self.setVirtualRight(np.concatenate((self.getVirtualRight(), neighbor)))
	
	def deleteLeftVirtualNeighbor(self, Ray:Ray):
		self.setVirtualLeft(np.delete(self.getVirtualLeft(), np.where(self.getVirtualLeft() == Ray)))

	def deleteRightVirtualNeighbor(self, Ray:Ray):
		self.setVirtualRight(np.delete(self.getVirtualRight(), np.where(self.getVirtualLeft() == Ray)))

	def isOutside(self, Ray:Ray):
		return Ray.getPos().getX() > self.X or Ray.getPos().getX() < 0 or Ray.getPos().getY() > self.Y or Ray.getPos().getY() < 0
	
	



	
	






	

	


	



            
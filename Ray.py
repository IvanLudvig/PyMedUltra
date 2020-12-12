import json
import math
import numpy as np
from Vector2 import Vector2
class Ray:
	def __init__(self,pos:Vector2=Vector2(),velocity:Vector2=Vector2(),material=-1,intensity=1.0,
		nextEncounter=math.inf,obstacle_number = 0,vertice_number =0,left=None,
		right=None,invalid=0,virtual_neighbors_left=np.array([]),virtual_neighbors_right=np.array([])):
		conf = 'res/config.json'
		with open(conf) as jf:
			configuration = json.load(jf)
			self.VISIBILITY_THRESHOLD = configuration["Constants"]["VISIBILITY_THRESHOLD"]
			self.SENSORS = configuration["Constants"]["SENSORS"]
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
	
	def detVirtualRight(self, virtual_neighbors_right):
		self.virtual_neighbors_right = virtual_neighbors_right
	
	

	



            
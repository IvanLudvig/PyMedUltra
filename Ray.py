from __future__ import annotations
import json
import math
import numpy as np
from Vector2 import Vector2
from Obstacle import Obstacle


class Ray:
    def __init__(self, pos: Vector2 = Vector2(), velocity: Vector2 = Vector2(), material=-1, intensity=1.0,
                 nextEncounter=math.inf, obstacle_number=0, vertice_number=0, left=None,
                 right=None, invalid=0, virtual_neighbors_left=np.array([]), virtual_neighbors_right=np.array([])):
        conf = 'res/config.json'
        with open(conf) as jf:
            configuration = json.load(jf)
            self.VISIBILITY_THRESHOLD = configuration["Constants"]["VISIBILITY_THRESHOLD"]
            self.SENSORS = configuration["Constants"]["SENSORS"]
            self.X = configuration["Constants"]["X"]
            self.Y = configuration["Constants"]["Y"]
            self.MINLEN = configuration["Constants"]["MINLEN"]
            self.DETERIORATION = configuration["Constants"]["DETERIORATION"]
        self.pos = Vector2()
        self.velocity = Vector2()
        self.material = material
        self.intensity = intensity
        self.nextEncounter = nextEncounter
        self.obstacle_number = obstacle_number
        self.vertice_number = vertice_number
        self.left = left
        self.right = right
        self.invalid = invalid
        self.virtual_neighbors_left = virtual_neighbors_left
        self.virtual_neighbors_right = virtual_neighbors_right

    def getPos(self) -> Vector2:
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
        self.nextEncounter = nextEncounter

    def setObstacleNumber(self, obstacle_number):
        self.obstacle_number = obstacle_number

    def setVerticeNumber(self, vertice_number):
        self.vertice_number = vertice_number

    def setLeft(self, left):
        self.left = left

    def setRight(self, right):
        self.right = right

    def setVirtualLeft(self, virtual_neighbors_left):
        self.virtual_neighbors_left = virtual_neighbors_left

    def setVirtualRight(self, virtual_neighbors_right):
        self.virtual_neighbors_right = virtual_neighbors_right

    def setInvalid(self, invalid):
        self.invalid = invalid

    def getPosAfterStep(self, step: float) -> Vector2:
        return Vector2(self.pos.getX() + self.velocity.getX() * step, self.pos.getY() + self.velocity.getY() * step)

    def getTime(self, dist, relativeSpeed) -> float:
        if self.material >= 0:
            return math.fabs(dist / relativeSpeed)
        else:
            return math.fabs(dist)

    def update(self, timeStep, relativeSpeed):
        self.pos.setX(
            self.pos.getX() + self.velocity.getX() * timeStep * (relativeSpeed if self.material >= 0 else 1.0))
        self.pos.setY(
            self.pos.getY() + self.velocity.getY() * timeStep * (relativeSpeed if self.material >= 0 else 1.0))
        if (self.nextEncounter < -0.5) or (self.nextEncounter == math.inf):
            return
        self.nextEncounter -= timeStep

    def getReflected(self, obstacle: Obstacle):
        vel, intensity = Vector2().getReflected(A=obstacle.getPos(self.vertice_number),
                                                B=obstacle.getPos(self.vertice_number + 1),
                                                velocity=self.velocity, relativeSpeed=obstacle.getRelativeSpeed(),
                                                intensity=self.intensity)
        return Ray(Vector2(self.pos.getX() - (1.00015 * self.velocity.getX()),
                           self.pos.getY() - (1.00015 * self.velocity.getY())), vel, intensity)

    def getRefracted(self, obstacle: Obstacle) -> Ray:
        vel, intensity = Vector2().getRefracted(A=obstacle.getPos(self.vertice_number),
                                                B=obstacle.getPos(self.vertice_number + 1),
                                                velocity=self.velocity, relativeSpeed=obstacle.getRelativeSpeed(),
                                                intensity=self.intensity)
        return Ray(Vector2(self.pos.getX() + (1.00015 * self.velocity.getX()),
                           self.pos.getY() + (1.00015 * self.velocity.getY())), vel, intensity)

    def addLeftVirtualNeighbor(self, neighbor: Ray) -> None:
        self.setVirtualLeft(np.concatenate((self.getVirtualLeft(), neighbor)))

    def addRightVirtualNeighbor(self, neighbor: Ray) -> None:
        self.setVirtualRight(np.concatenate((self.getVirtualRight(), neighbor)))

    def deleteLeftVirtualNeighbor(self, ray: Ray) -> None:
        self.virtual_neighbors_left = np.where(self.virtual_neighbors_left == ray, self.virtual_neighbors_left, None)
        # self.setVirtualLeft(np.delete(self.getVirtualLeft(), np.where(self.getVirtualLeft() == ray)))

    def deleteRightVirtualNeighbor(self, ray: Ray) -> None:
        self.virtual_neighbors_right = np.where(self.virtual_neighbors_right == ray, self.virtual_neighbors_right, None)
        # self.setVirtualRight(np.delete(self.getVirtualRight(), np.where(self.getVirtualLeft() == ray)))

    def isOutside(self, ray: Ray) -> bool:
        return ray.getPos().getX() > self.X or ray.getPos().getX() < 0 or ray.getPos().getY() > self.Y or ray.getPos().getY() < 0

    def virtualHandler(self, ray: Ray, isRightNeighbor: bool) -> None:
        if (ray.getMaterial() == self.getMaterial() and Vector2().scalar(ray.getVelocity(),
                                                                         self.getVelocity()) > 0 and Vector2().length(
            ray.getPos(), self.getPos()) < 5 * self.MINLEN):
            if self.getLeft() and isRightNeighbor:
                ray.setRight(self)
                self.setLeft(ray)
            elif not self.getRight() and not isRightNeighbor:
                ray.setLeft(self)
                self.setRight(ray)
                self.setNextEncounter(math.inf)

    def restoreWavefront(self, reflected: Ray, refracted: Ray) -> None:
        for i in range(self.virtual_neighbors_left.shape[0]):
            self.virtual_neighbors_left[i].virtualHandler(reflected, False)
            self.virtual_neighbors_left[i].virtualHandler(refracted, False)
        for i in range(self.virtual_neighbors_right.shape[0]):
            self.virtual_neighbors_right[i].virtualHandler(reflected, True)
            self.virtual_neighbors_right[i].virtualHandler(refracted, True)

    def killLeft(self) -> None:
        for i in range(self.virtual_neighbors_left.shape[0]):
            self.virtual_neighbors_left[i].deleteLeftVirtualNeighbor(self)

    def killRight(self) -> None:
        for i in range(self.virtual_neighbors_right.shape[0]):
            self.virtual_neighbors_right[i].deleteRightVirtualNeighbor(self)

    def checkInvalid(self) -> None:
        if ((self.intensity < self.VISIBILITY_THRESHOLD) or self.isOutside(self)
                or (not self.left and not self.right and not (self.virtual_neighbors_left.shape[0]) and not (
                        self.virtual_neighbors_right.shape[0]))):
            self.invalid = 1
        if self.invalid > 0:
            if self.left:
                self.left.right = None
            if self.right:
                self.right.left = None
        self.killLeft()
        self.killRight()
        self.virtual_neighbors_left = np.array([])
        self.virtual_neighbors_right = np.array([])

    def clearNeighbours(self) -> None:
        nulls_exist = True
        while nulls_exist:
            nulls_exist = False
        for i in range(self.virtual_neighbors_left.shape[0]):
            if not nulls_exist and not self.virtual_neighbors_left[i]:
                self.virtual_neighbors_left = np.delete(self.virtual_neighbors_left, i)
                nulls_exist = True
        nulls_exist = True
        while nulls_exist:
            nulls_exist = False
        for i in range(self.virtual_neighbors_right.shape[0]):
            if not nulls_exist and not self.virtual_neighbors_right[i]:
                self.virtual_neighbors_right = np.delete(self.virtual_neighbors_right, i)
                nulls_exist = True

    def deteriorate(self):
        self.intensity *= self.DETERIORATION

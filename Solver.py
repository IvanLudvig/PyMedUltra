import json
import math

import numpy as np

from Dot import Dot
from Obstacle import Obstacle
from Ray import Ray
from Vector2 import Vector2


class Solver:

    def __init__(self):
        conf = 'res/config.json'
        with open(conf) as jf:
            configuration = json.load(jf)
            self.OBSTACLES = configuration['OBSTACLES']['NUMBER_OF_OBSTACLES']
            self.VERTICES = configuration['Constants']['VERTICES']
            self.DOTS = configuration['DOTS']['NUMBER_OF_DOTS']
            self.SENSORS = configuration['Constants']['SENSORS']
            self.POINTS_IN_DOT_WAVEFRONT = configuration['Constants']['POINTS_IN_DOT_WAVEFRONT']
            self.X = configuration['Constants']['X']
            self.Y = configuration['Constants']['Y']
            self.DX_SENSORS = configuration['Constants']['DX_SENSORS']
            self.ZERO = configuration['Constants']['ZERO']

            self.nodesNum = 0
            self.obstacles = np.array([])
            self.dots = np.array([])
            self.sensors = np.array([])
            self.rays = np.array([])

            self.initObstacles(configuration)
            self.initDots(configuration)

    def initObstacles(self, configuration):
        for i in range(self.OBSTACLES):
            obstacle = Obstacle()
            for j in range(self.VERTICES):
                obstacle.addPos(Vector2(configuration['OBSTACLES']['X'][i], configuration['OBSTACLES']['Y'][i]))
            relativeSpeed = configuration['OBSTACLES']['RELATIVE_SPEED']
            obstacle.setCRel(relativeSpeed)
            obstacle.addPos(obstacle.getPos(0))
            self.obstacles = np.append(self.obstacles, obstacle)

    def initDots(self, configuration):
        for i in range(self.DOTS):
            dot = Dot(Vector2(configuration['DOTS']['X'][i], configuration['DOTS']['Y'][i]),
                      configuration['DOTS']['B'][i])
            self.dots = np.append(self.dots, dot)

    def propagate(self):
        for i in range(self.SENSORS):
            x = self.X / 2 - self.DX_SENSORS * (self.SENSORS / 2 - i)
            y = self.Y * 0.999
            # sensor = Sensor(Vector2(x, y))
            # self.sensors = np.append(self.sensors, sensor)

        for sensor in self.sensors:
            self.initExplosion(sensor.getPos())
            self.resetTime()
            while self.finishTime > 0:
                self.step()

    def initExplosion(self, pos):
        n = self.POINTS_IN_DOT_WAVEFRONT * 2

        for i in range(n):
            angle = 2 * math.pi * i / n
            velocity = Vector2(math.cos(angle), math.sin(angle))
            self.rays = np.append(self.rays, Ray(pos, velocity))

        for i in range(1, n):
            self.rays[i].setLeft(self.rays[i - 1])
            self.rays[i].setRight(self.rays[i + 1])

        self.rays[0].setLeft(self.rays[n - 1])
        self.rays[0].setRight(self.rays[1])
        self.rays[n - 1].setLeft(self.rays[n - 2])
        self.rays[n - 1].setRight(self.rays[0])

    def resetTime(self):
        self.startTime = self.SENSORS * self.DX_SENSORS * 0.1
        self.finishTime = 2.0 * self.Y

    def step(self):
        for ray in self.rays:
            encounters = 0
            if ray.getNextEncounter() == math.inf:
                encounters += self.checkObstacles(ray)
                if ray.getRight():
                    encounters += self.checkDots(ray)
                    
                if encounters == 0:
                    ray.setNextEncounter(-1)

    def checkObstacles(self, ray):
        encounters = 0

    def checkDots(self, ray):
        encounters = 0

    def handleReflection(self):
        delta = float(0.5)
        for i in range(self.nodesNum):
            if (self.rays[i].getNextEncounter() < self.ZERO) and (self.rays[i].getNextEncounter > -delta):
                if self.rays[i].getObstacleNumber() >= 0:
                    reflected = Ray(self.rays[i].getReflected(self.obstacles[self.rays[i].getObstacleNumber()]))
                    refracted = Ray(self.rays[i].getRefracted(self.obstacles[self.rays[i].getObstacleNumber()]))
                    if reflected.getIntensity() == -1:
                        self.rays[i].setInvalid(1)
                    else:
                        # real neighbors always turn to ghost ones -
                        # reflected go to the other direction, refracted are in another material

                        if self.rays[i].getLeft():
                            left = Ray(self.rays[i].getLeft())
                            reflected.addLeftVirtualNeighbor(left)
                            refracted.addLeftVirtualNeighbor(left)
                            left.addRightVirtualNeighbor(reflected)
                            left.addLeftVirtualNeighbor(refracted)
                            self.rays[i].setLeft(left)

                        if self.rays[i].getRight():
                            right = Ray(self.rays[i].getRight())
                            reflected.addRightVirtualNeighbor(right)
                            refracted.addRightVirtualNeighbor(right)
                            right.addRightVirtualNeighbor(reflected)
                            right.addLeftVirtualNeighbor(refracted)
                            self.rays[i].setRight(right)

                    self.rays[i].restoreWavefront(reflected, refracted)

                elif self.rays[i].getObstacleNumber() == -1:  # encountering a dot obstacle
                    sina = float(-self.rays[i].getVelocity().getY())
                    cosa = float(-self.rays[i].getVelocity().getX())
                    if cosa > 0:
                        alpha = float(np.arcsin(sina))
                    else:
                        alpha = float(math.pi - float(np.arcsin(sina)))

                    dalpha = float(math.pi / (self.POINTS_IN_DOT_WAVEFRONT - 1))
                    alpha += math.pi / 2
                    oldNodesNum = self.nodesNum
                    for j in range(self.POINTS_IN_DOT_WAVEFRONT):
                        n = Ray(Vector2(self.dots[self.rays[i].getVerticeNumber()].getPos().getX()+np.cos(alpha)*0.01,
                                        self.dots[self.rays[i].getVerticeNumber()].getPos().getY()+np.sin(alpha)*0.01),
                                Vector2(np.cos(alpha), np.sin(alpha)),
                                1.0*self.dots[self.rays[i].getVerticeNumber()].getBrightness())
                        self.rays[self.nodesNum] = n
                        self.nodesNum += 1
                        alpha -= dalpha

                    for j in range(1, self.POINTS_IN_DOT_WAVEFRONT - 1):
                        self.rays[oldNodesNum + j].setLeft(self.rays[oldNodesNum + j - 1])
                        self.rays[oldNodesNum + j].setRight(self.rays[oldNodesNum + j + 1])

                    self.rays[oldNodesNum].setRight(self.rays[oldNodesNum + 1])
                    self.rays[self.nodesNum - 1].setLeft(self.rays[self.nodesNum - 2])
                    self.rays[i].setNextEncounter(math.inf)




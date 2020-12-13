import json
import math

import numpy as np

from Dot import Dot
from Obstacle import Obstacle
from Ray import Ray
from Record import Record
from Sensor import Sensor
from Vector2 import Vector2, doIntersect, distanceToSegment


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
            self.DT_DIGITIZATION = configuration['Constants']['DT_DIGITIZATION']
            self.T_MULTIPLIER = configuration['Constants']['T_MULTIPLIER']
            self.DT_DETERIORATION = configuration['Constants']['DT_DETERIORATION']
            self.WRITE_TO_CSV = configuration['ROOTS']['WRITE_TO_CSV']

            self.raysNum = 0
            self.deteriorationTime = 0
            self.totalTime = 0
            self.currentSensor = 0
            self.obstacles = np.array([])
            self.dots = np.array([])
            self.sensors = np.array([])
            self.rays = np.array([])

            self.initObstacles(configuration)
            self.initDots(configuration)
        self.propagate()

    def initObstacles(self, configuration):
        for i in range(self.OBSTACLES):
            obstacle = Obstacle()
            for j in range(self.VERTICES):
                obstacle.addPos(Vector2(configuration['OBSTACLES']['X'][i], configuration['OBSTACLES']['Y'][i]))
            relativeSpeed = configuration['OBSTACLES']['RELATIVE_SPEED']
            obstacle.setRelativeSpeed(relativeSpeed)
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
            sensor = Sensor()
            sensor.setPos(Vector2(x, y))
            self.sensors = np.append(self.sensors, sensor)

        for sensor in self.sensors:
            print('SENSOR', self.currentSensor)
            with open(self.WRITE_TO_CSV.format(self.currentSensor, self.currentSensor), "w") as file:
                file.write("")
            self.initExplosion(sensor.getPos())
            self.resetTime()
            i = 0
            while self.finishTime > 0:
                self.step()
                if i % 500 == 0:
                    print('iter', i)
                i += 1
            self.currentSensor += 1

    def initExplosion(self, pos):
        n = self.POINTS_IN_DOT_WAVEFRONT * 2

        for i in range(n):
            angle = 2 * math.pi * i / n
            velocity = Vector2(math.cos(angle), math.sin(angle))
            self.rays = np.append(self.rays, Ray(pos, velocity))
            self.raysNum += 1

        for i in range(1, n - 1):
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
        timeStep = self.DT_DIGITIZATION * self.T_MULTIPLIER
        for ray in self.rays:
            encounters = 0
            if ray.getNextEncounter() == math.inf:
                encounters += self.checkObstacles(ray)
                if ray.getRight():
                    encounters += self.checkDots(ray)
                if encounters == 0:
                    ray.setNextEncounter(-1)
            if ray.getNextEncounter() > self.ZERO:
                timeStep = min(timeStep, ray.getNextEncounter())

        for ray in self.rays:
            ray.update(timeStep, self.obstacles[ray.getMaterial()].getRelativeSpeed())

        self.handleReflection()
        self.fixNodes()

        self.deteriorationTime += timeStep
        while self.deteriorationTime > self.DT_DETERIORATION:
            self.deteriorate()
            self.deteriorationTime -= self.DT_DETERIORATION

        self.totalTime += timeStep
        while self.totalTime > self.DT_DETERIORATION:
            if self.startTime < 0:
                self.writeToCSV()
            self.totalTime -= self.DT_DETERIORATION
            self.startTime -= self.DT_DETERIORATION
            self.finishTime -= self.DT_DETERIORATION

    def checkObstacles(self, ray):
        encounters = 0
        for i, obstacle in enumerate(self.obstacles):
            for vertex in range(self.VERTICES - 1):
                intersect, distance = doIntersect(obstacle.getPos(vertex), obstacle.getPos(vertex + 1), ray.getPos(),
                                                  ray.getVelocity())
                if intersect:
                    time = ray.getTime(distance, self.obstacles[ray.getMaterial()].getRelativeSpeed())
                    if time < ray.getNextEncounter():
                        ray.setNextEncounter(time)
                        ray.setObstacleNumber(i)
                        ray.setVerticeNumber(vertex)
                        encounters += 1
        return encounters

    def checkDots(self, ray):
        encounters = 0

        rayPos = ray.getPosAfterStep(10)
        rightRayPos = ray.getRight().getPosAfterStep(10)
        rayNextPos = ray.getPosAfterStep(1000)
        rightRayNextPos = ray.getRight().getPosAfterStep(1000)

        for i, dot in enumerate(self.dots):
            if dot.getPos().isPointInRect(rayPos, rightRayPos, rayNextPos, rightRayNextPos):
                distance = distanceToSegment(ray.getPos(), ray.getRight().getPos(), dot.getPos())
                time = ray.getTime(distance, self.obstacles[ray.getMaterial()].getRelativeSpeed())
                if time < ray.getNextEncounter():
                    ray.setNextEncounter(time)
                    ray.setObstacleNumber(-1)
                    ray.setVerticeNumber(i)
                    encounters += 1

        for sensor in self.sensors:
            if sensor.getPos().isPointInRect(rayPos, rightRayPos, rayNextPos, rightRayNextPos):
                distance = distanceToSegment(ray.getPos(), ray.getRight().getPos(), sensor.getPos())
                time = ray.getTime(distance, self.obstacles[ray.getMaterial()].getRelativeSpeed())
                if time < ray.getNextEncounter():
                    sensor.addRecord(Record(-time, ray.getIntensity(), 1.0 / ray.getVelocity().getY()))

        return encounters

    def handleReflection(self):
        delta = float(0.5)
        for i in range(self.raysNum):
            if (self.rays[i].getNextEncounter() < self.ZERO) and (self.rays[i].getNextEncounter > -delta):
                print('reflect')
                if self.rays[i].getObstacleNumber() >= 0:
                    reflected = self.rays[i].getReflected(self.obstacles[self.rays[i].getObstacleNumber()])
                    refracted = self.rays[i].getRefracted(self.obstacles[self.rays[i].getObstacleNumber()])
                    if reflected.getIntensity() == -1:
                        self.rays[i].setInvalid(1)
                    else:
                        # real neighbors always turn to ghost ones -
                        # reflected go to the other direction, refracted are in another material
                        if self.rays[i].getLeft():
                            left = self.rays[i].getLeft()
                            reflected.addLeftVirtualNeighbor(left)
                            refracted.addLeftVirtualNeighbor(left)
                            left.addRightVirtualNeighbor(reflected)
                            left.addRightVirtualNeighbor(refracted)
                            self.rays[i].setLeft(left)

                        if self.rays[i].getRight():
                            right = self.rays[i].getRight()
                            reflected.addRightVirtualNeighbor(right)
                            refracted.addRightVirtualNeighbor(right)
                            right.addRightVirtualNeighbor(reflected)
                            right.addRightVirtualNeighbor(refracted)
                            self.rays[i].setRight(right)

                    self.rays[self.raysNum] = reflected
                    self.raysNum += 1
                    self.rays[self.raysNum] = refracted
                    self.raysNum += 1
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
                    oldNodesNum = self.raysNum
                    for j in range(self.POINTS_IN_DOT_WAVEFRONT):
                        n = Ray(
                            Vector2(self.dots[self.rays[i].getVerticeNumber()].getPos().getX() + np.cos(alpha) * 0.01,
                                    self.dots[self.rays[i].getVerticeNumber()].getPos().getY() + np.sin(alpha) * 0.01),
                            Vector2(np.cos(alpha), np.sin(alpha)),
                            1.0 * self.dots[self.rays[i].getVerticeNumber()].getBrightness())
                        self.rays[self.raysNum] = n
                        self.raysNum += 1
                        alpha -= dalpha

                    for j in range(1, self.POINTS_IN_DOT_WAVEFRONT - 1):
                        self.rays[oldNodesNum + j].setLeft(self.rays[oldNodesNum + j - 1])
                        self.rays[oldNodesNum + j].setRight(self.rays[oldNodesNum + j + 1])

                    self.rays[oldNodesNum].setRight(self.rays[oldNodesNum + 1])
                    self.rays[self.raysNum - 1].setLeft(self.rays[self.raysNum - 2])
                    self.rays[i].setNextEncounter(math.inf)

    def fixNodes(self):
        for i in range(self.raysNum):
            self.rays[i].checkInvalid()

            if self.rays[i].getInvalid():
                for sensor in self.sensors:
                    for record in sensor.getRecord():
                        if record.getRay() == self.rays[i]:
                            sensor.clearRecord()
                self.rays[i] = None

        cleared = False
        while not cleared:
            while (not self.rays[self.raysNum - 1]) and (self.raysNum > 0):
                self.raysNum -= 1
            cleared = True
            for i in range(self.raysNum):
                if not self.rays[i]:
                    self.raysNum -= 1
                    self.rays[i] = self.rays[self.raysNum]
                    cleared = False
                    break

        for ray in self.rays:
            ray.clearNeighbours()

    def deteriorate(self):
        for ray in self.rays:
            ray.deteriorate()
        for sensor in self.sensors:
            sensor.deteriorate()

    def writeToCSV(self):
        for sensor in self.sensors:
            sensor.recordToCSV(self.currentSensor)
        with open(self.WRITE_TO_CSV.format(self.currentSensor, self.currentSensor), "a") as file:
            file.write("\n")

import json
import numpy as np

from Dot import Dot
from Obstacle import Obstacle
from Vector2 import Vector2


class Solver:

    def __init__(self):
        conf = 'res/config.json'
        with open(conf) as jf:
            configuration = json.load(jf)
            self.OBSTACLES = configuration['OBSTACLES']['NUMBER_OF_OBSTACLES']
            self.VERTICES = configuration['Constants']['VERTICES']
            self.DOTS = configuration['DOTS']['NUMBER_OF_DOTS']
            self.obstacles = np.array([])
            self.dots = np.array([])
            self.sensors = np.array([])
            self.nodes = np.array([])

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

    def initDots(self, configutation):
        for i in range(self.DOTS):
            dot = Dot(Vector2(configutation['DOTS']['X'][i], configutation['DOTS']['Y'][i]),
                      configutation['DOTS']['B'][i])
            self.dots = np.append(self.dots, dot)

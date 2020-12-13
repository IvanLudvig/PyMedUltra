import json
import numpy as np
from Vector2 import Vector2


class Obstacle:
    def __init__(self, x=0, y=0):
        conf = 'res/config.json'
        with open(conf) as jf:
            configuration = json.load(jf)
            self.relativeSpeed = configuration['OBSTACLES']['RELATIVE_SPEED']
        self.pos = []

    def getPos(self, i: int) -> Vector2:
        return self.pos[i]

    def setPos(self, j: int, pos: Vector2) -> None:
        self.pos[j] = pos

    def getCRel(self) -> float:
        return self.relativeSpeed

    def setCRel(self, relativeSpeed: float) -> None:
        self.relativeSpeed = relativeSpeed

    def addPos(self, pos: Vector2) -> None:
        self.pos.append(pos)

import json
import math
import numpy as np
from Vector2 import Vector2
from Record import Record


class Sensor:
    def __init__(self):
        conf = 'res/config.json'
        with open(conf) as jf:
            configuration = json.load(jf)
            self.SENSORS = configuration["Constants"]["SENSORS"]
            self.DT_WIDTH = configuration["Constants"]["DT_WIDTH"]
            self.DT_CARRYING = configuration["Constants"]["DT_CARRYING"]
            self.WRITE_TO_CSV = configuration["ROOTS"]["WRITE_TO_CSV"]
            self.DT_DIGITIZATION = configuration["Constants"]["DT_DIGITIZATION"]
        self.pos = Vector2()
        self.record = []

    def getPos(self) -> Vector2:
        return self.pos

    def getRecord(self) -> list:
        return self.record

    def setPos(self, pos: Vector2) -> None:
        self.pos = pos

    def setRecord(self, record: list) -> None:
        self.record = record

    def clearRecord(self) -> None:
        self.record = []

    def addRecord(self, record: Record) -> None:
        self.record.append(record)

    def deteriorate(self) -> None:
        for i in self.record:
            i.deteriorate()

    def signal(self, t: float, fc: float) -> float:
        return math.sin(math.pi * t / self.DT_WIDTH) * math.sin(math.pi * t / self.DT_WIDTH) * math.sin(
            2 * math.pi * t / self.DT_CARRYING * fc)

    def recordToCSV(self, number: int) -> None:
        signal = 0
        for r in self.record:
            if (r.getTime() > 0):
                signal += r.getBrightness() * self.signal(r.getTime(), r.getFrequencyCorrection())
            r.setTime(r.getTime() + self.DT_DIGITIZATION)
        with open(self.WRITE_TO_CSV.format(number, number), "w") as file:
            file.write(round(signal, 2) + " ")
        nulls_exist = True
        while (nulls_exist):
            nulls_exist = False
            for j in range(len(self.record)):
                if (self.record[j].getTime() > self.DT_WIDTH):
                    self.record = np.delete(self.record, j)
                    nulls_exist = True
                    break

        def addWriting(w: Record) -> None:
            self.record = np.concatenate(self.record, w)

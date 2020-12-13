import json
from Ray import Ray


class Record:
    def __init__(self, time: float, brightness: float, frequency_correction: float):
        self.time = time
        self.brightness = brightness
        self.frequency_correction = frequency_correction
        conf = 'res/config.json'
        with open(conf) as jf:
            configuration = json.load(jf)
        self.DETERIORATION = configuration["Constants"]["DETERIORATION"]
        self.ray = Ray()

    def getTime(self) -> float:
        return self.time

    def getBrightness(self) -> float:
        return self.brightness

    def getFrequencyCorrection(self) -> float:
        return self.frequency_correction

    def getNode(self) -> Ray:
        return Ray

    def setTime(self, time: float) -> None:
        self.time = time

    def setBrightness(self, brightness: float) -> None:
        self.brightness = brightness

    def setFrequencyCorrection(self, frequency_correction: float) -> None:
        self.frequency_correction = frequency_correction

    def setNode(self, ray: Ray) -> None:
        self.ray = ray

    def deteriorate(self) -> None:
        self.brightness *= self.DETERIORATION

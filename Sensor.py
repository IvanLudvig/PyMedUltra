import json


class Sensor:
    def __init__(self):
        conf = 'res/config.json'
        with open(conf) as jf:
            configuration = json.load(jf)
            self.SENSORS = configuration["Constants"]["SENSORS"]
            self.DT_WIDTH = configuration["Constants"]["DT_WIDTH"]
            self.DT_CARRYING = configuration["Constants"]["DT_CARRYING"]

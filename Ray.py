import json
from Vector2 import Vector2
class Ray:
    def __init__(self,pos:Vector2=Vector2(),
		   velocity:Vector2=Vector2(),
		   material:int,
		   intensity:float,
		   nextEncounter:float,
		   obstacle_number:int,
		   vertice_number:int,
		   left:Ray,
		   right:Ray,
		   kill_marked:invalid,
		   const std::vector<Node *> &virtual_neighbors_left,
		   const std::vector<Node *> &virtual_neighbors_right):
        conf = 'res/config.json'
        with open(conf) as jf:
            configuration = json.load(jf)
            self.VISIBILITY_THRESHOLD = configuration["Constants"]["VISIBILITY_THRESHOLD"]
            self.SENSORS = configuration["Constants"]["SENSORS"]
        self.pos = Vector2()
        self.velocity = Vector2()


            
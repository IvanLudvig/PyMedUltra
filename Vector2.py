import math
class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def setX(self, x:float):
        self.x = x

    def setY(self, y:float):
        self.y = y

    def getX(self):
        return self.x 

    def getY(self):
        return self.y
    
    def scalar(self, A:Vector2, B:Vector2) -> float:
        return A.getX() * B.getX() + A.getY() * B.getY()
    
    def length(self, A:Vector2, B:Vector2) -> float:
        tmp = Vector2((A.getX()-B.getX()), (A.getY()-B.getY()))
        return math.sqrt(self.scalar(tmp, tmp))
    
    def area(self, A:Vector2, B:Vector2, C:Vector2)->float:
        return (B.getX() - A.getX()) * (C.getY() - A.getY()) - (B.getY() - A.getY()) * (C.getX() - A.getX())
    
    def doIntersact(self, A:Vector2, B:Vector2, C:Vector2, D:Vector2, Result:Vector2)->bool:
        if  not (self.area(A, D, B) * self.area(A, B, C) > 0 and self.area(D, B, C) * self.area(D, C, A) > 0):
            return False




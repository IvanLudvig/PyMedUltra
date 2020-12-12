import math
import json
class Vector2:
    def __init__(self, x=0, y=0):
        conf = 'res/config.json'
        with open(conf) as jf:
            configuration = json.load(jf)
            self.ZERO = configuration["Constants"]["ZERO"]

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
        Temp = ((C.getY() - A.getY()) * (B.getX() - A.getX()) -
		(C.getX() - A.getX()) * (B.getY() - A.getY()))/((C.getX() - D.getX()) * (B.getY() - A.getY()) -
			(C.getY() - D.getY()) * (B.getX() - A.getX()))
        Result.setX(C.getX() + (C.getX() - D.getX()) * Temp)
        Result.setY(C.getY() + (C.getY() - D.getY()) * Temp)
        return True

    def doIntersect(self, A:Vector2, B:Vector2, C:Vector2, V:Vector2, distanceToIntersection:float)->bool:
        D = Vector2(C.getX() + V.getX() * 1000, C.getY() + V.getY() * 1000)
        if not (self.area(A, D, B) * self.area(A, B, C) > 0 and self.area(D, B, C) * self.area(D, C, A) > 0):
            return False
        distanceToIntersection = ((C.getY() - A.getY()) * (B.getX() - A.getX()) -
		(C.getX() - A.getX()) * (B.getY() - A.getY()))/((C.getX() - D.getX()) * (B.getY() - A.getY()) -
			(C.getY() - D.getY()) * (B.getX() - A.getX())) * self.length(C, D)
        return True

    def isPointInRect(self,P:Vector2, A:Vector2, B:Vector2, C:Vector2, D:Vector2,)->bool:
        Area1 = self.area(P, A, B) > -self.ZERO
        Area2 = self.area(P, B, C) > -self.ZERO
        Area3 = self.area(P, C, D) > -self.ZERO
        Area4 = self.area(P, D, A) > -self.ZERO
        return (Area1 == Area2 and Area2 == Area3 and Area3 == Area4)

    def distanceToSegment(self, a:Vector2, b:Vector2, va:Vector2, vb:Vector2, c:Vector2 )->float:
        o = Vector2((a.getX() + b.getX())/2, (a.getX() + b.getY())/2)
        dist = self.length(o, c)
        return dist



    def getReflected(self,A:Vector2, B:Vector2, velocity:Vector2, relativeSpeed:float, intensity:float)->Vector2:
        sinA = -velocity.getY()
        cosA = velocity.getX()
        sinB = (B.getY() - A.getY()) / self.length(A, B)
        cosB = (B.getX() - A.getX()) / self.length(A, B)
        if (cosB > 1.0 or cosB < -1.0):
            intensity = -1
            return Vector2()
        z1 = 1 * cosA
        z2 = relativeSpeed * cosB
        intensity *= math.fabs((z2 - z1) / (z2 + z1))
        return Vector2(cosA * (cosB * cosB - sinB * sinB) - 2.0 * sinA * sinB * cosB,
				   sinA * (cosB * cosB - sinB * sinB) + 2.0 * cosA * sinB * cosB)


    def getRefracted(self,A:Vector2, B:Vector2, Velocity:Vector2, relativeSpeed:float, intensity:float)->Vector2:
        sinG = (B.getY() - A.getY())/self.length(A, B)
        cosG = (B.getX() - A.getX())/self.length(A, B)
        sinF = Velocity.getY()
        cosF = Velocity.getX()
        cosA = cosG * cosF + sinG * sinF
        sinA = sinG * cosF - sinF * cosG
        cosB = relativeSpeed * cosA
        if (cosB > 1.0 or cosB < -1.0):
            intensity = -1
            return Vector2()
        sinB = math.sqrt(1 - cosB * cosB)
        if (sinA < 0):
            sinB *= -1
        z1 = 1 * cosA
        z2 = relativeSpeed * cosB
        intensity *= math.fabs(2 * z2 / (z2 + z1))
        return Vector2(cosG * cosB + sinG * sinB, sinG * cosB - cosG * sinB)


        









    










    
        
    



from abc import ABC , abstractclassmethod
import math

class BaseExercise(ABC):
    def __init__(self):
        self.reps=0
        self.stage=None

    def calculate_angle(self, a, b, c):
        ax = a[0] - b[0]
        ay = a[1] - b[1]

        cx = c[0] - b[0]
        cy = c[1] - b[1]

        dot = ax * cx + ay * cy

        mag_a = math.sqrt(ax ** 2 + ay ** 2)
        mag_c = math.sqrt(cx ** 2 + cy ** 2)

        if mag_a * mag_c == 0:
            return 0.0

        cos_angle = dot / (mag_a * mag_c)
        cos_angle = max(-1.0, min(1.0, cos_angle))

        return math.degrees(math.acos(cos_angle))
    
    def get_point(self,landmarks,idx):
        p=landmarks[idx]
        return(p.x,p.y)

    @abstractclassmethod
    def process(Self,landmarks):
        pass

    @abstractclassmethod
    def reset(self):
        pass
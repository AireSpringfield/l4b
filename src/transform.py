class Transform(object):
    pass

class Rotate(Transform):
    angle: float



class RotateX(Rotate):
    def __init__(self, angle):
        self.angle = angle

    def __repr__(self):
        return 'RotateX({})'.format(self.angle)

class RotateY(Rotate):
    def __init__(self, angle):
        self.angle = angle

    def __repr__(self):
        return 'RotateY({})'.format(self.angle)

class RotateZ(Rotate):
    def __init__(self, angle):
        self.angle = angle

    def __repr__(self):
        return 'RotateZ({})'.format(self.angle)



class Lookat(Transform):
    def __init__(self, target):
        self.target = target
    def __repr__(self):
        return 'Lookat({})'.format(self.target)


class Forward(Transform):
    def __init__(self, length):
        self.length = length


    def __repr__(self):
        return 'Forward({})'.format(self.length)


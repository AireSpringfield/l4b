import sys
sys.path.insert(0, r'F:\l4b\src')

from dataclasses import dataclass
from lsystem import *
from lstring import *
from transform import *
import turtle
import math
import mathutils

import importlib
importlib.reload(turtle)

dt = 0.2



@dataclass
class Apex(Module):
    age: float
    sgn: int

    def production_1(self):
        if self.age >= 1.0:
            self.age -= 1.0
            self.sgn *= -1
            return [FlowerInternode(0, [RotateZ(self.sgn*60), RotateY(30)]), Flower(0)], Internode(0, [RotateY(5)]), self
        else:
            self.age += dt
            return self


pa = Predecessor(Apex)
Apex.productions[pa] = Apex.production_1


@dataclass
class Flower(Module):
    age: float

    def production_1(self):
        self.age += dt
        return self

    def draw(self):
        scale = 1.0 - math.exp(-self.age / 1.0)
        turtle.draw_object('Flower', scale)

pk = Predecessor(Flower)
Flower.productions[pk] = Flower.production_1

@dataclass
class Leaf(Module):
    age: float

    def production_1(self):
        self.age += dt
        return self

    def draw(self):
        scale = 1.0 - math.exp(-self.age / 15.0)
        angle = math.radians(50*scale)
        turtle.turtle_mat @= mathutils.Matrix.Rotation(angle, 4, 'Y')
        turtle.draw_object('Leaf', scale)

pk = Predecessor(Leaf)
Leaf.productions[pk] = Leaf.production_1

@dataclass
class Internode(Module):
    age: float
    transforms: list

    def production_1(self):
        self.age += dt
        return self

    def draw(self):
        length = 1.0 + max(1.0, self.age/2.0)
        self.transforms.append(Forward(length))
        end_turtle = turtle.turtle_mat.copy()
        for t in self.transforms:
            end_turtle @= turtle.matrixof(t)
        turtle.draw_curve(end_turtle.col[3], end_turtle.col[2])
        turtle.turtle_mat = end_turtle

pi = Predecessor(Internode)
Internode.productions[pi] = Internode.production_1

@dataclass
class FlowerInternode(Module):
    age: float
    transforms: list

    def production_1(self):
        self.age += dt
        return self

    def draw(self):
        length = 1.0 + max(2.0, self.age)
        self.transforms.append(Forward(length))
        end_turtle = turtle.turtle_mat.copy()
        for t in self.transforms:
            end_turtle @= turtle.matrixof(t)
        # Gravitropism
        factr = math.exp(-self.age/1.0)
        rot_quaternion = end_turtle.col[2].xyz.normalized().rotation_difference(mathutils.Vector((0,0,-1)))
        rot = rot_quaternion.slerp(mathutils.Quaternion(), factr)
        mat = rot.to_matrix()
        mat.resize_4x4()
        for i in range(3):
            end_turtle.col[i] = mat @ end_turtle.col[i]
        print(end_turtle)
        end_turtle.col[3].xyz += length * end_turtle.col[2].xyz

        turtle.draw_curve(end_turtle.col[3], end_turtle.col[2])
        turtle.turtle_mat = end_turtle

pi = Predecessor(FlowerInternode)
FlowerInternode.productions[pi] = FlowerInternode.production_1

lsys = Lsystem([[RotateZ(90), Leaf(0)], [RotateZ(270), Leaf(0)], Internode(5, []), Apex(0, 1)])


lsys.derive(20)
print(lsys.lstring)
turtle.interpret(lsys.lstring, 'Derive20')



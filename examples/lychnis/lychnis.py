import sys
code_folder = r'F:\l4b\src'  # Change your code folder path!
sys.path.insert(0, code_folder)

from dataclasses import dataclass
from lsystem import *
from lstring import *
from transform import *




@dataclass
class Apex(Module):
    age: int

    def __hash__(self):
        return id(self)

    def production_1(self):
        if self.age == 7:
            return Internode(8), \
                   [RotateY(+40), Leaf(0)], \
                   RotateZ(90), [RotateX(-30), Apex(0)], \
                   RotateZ(90), [RotateY(+40), Leaf(0)], \
                   RotateZ(90), [RotateX(-30), Apex(4)], \
                   Internode(3), Flower(0)
        elif self.age < 7:
            return Apex(self.age + 1)


pa = Predecessor(Apex)
Apex.productions[pa] = Apex.production_1


@dataclass
class Flower(Module):
    age: int

    def __hash__(self):
        return id(self)

    def production_1(self):
        self.age += 1
        return self

    def draw(self):
        if self.age >= 5:
            turtle.draw_object('FlowerBud')
        else:
            turtle.draw_object('Flower')


pk = Predecessor(Flower)
Flower.productions[pk] = Flower.production_1


@dataclass
class Internode(Module):
    age: int

    def __hash__(self):
        return id(self)

    def production_1(self):
        self.age += 1
        return self

    def draw(self):
        turtle.draw_internode_straight(self.age)

pi = Predecessor(Internode)
Internode.productions[pi] = Internode.production_1


@dataclass
class Leaf(Module):
    age: int

    def __hash__(self):
        return id(self)

    def production_1(self):
        self.age += 1
        return self

    def draw(self):
        turtle.draw_object('Leaf')

pl = Predecessor(Leaf)
Leaf.productions[pl] = Leaf.production_1


##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################

lsys = Lsystem([Apex(0)])
lsys.derive(20)

print(lsys.lstring)

import turtle
turtle.interpret(lsys.lstring, 'lychnis')

# When running in Blender for creating models, you can comment these out, because Blender does not have
# networkx installed in its Python intepreter by default 
# from tree import *
# print(typeof(lsys.lstring))
# tree = eval(lsys.lstring)
# tree.show()

# Need to execute in Blender!




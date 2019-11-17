import sys
code_folder = r'F:\l4b\src'  # Change your code folder path!
sys.path.insert(0, code_folder)

from dataclasses import dataclass
from lsystem import *
from lstring import *
from transform import *


@dataclass
class Florigen(Module):
    def production_1(self):
        return None
p1 = Predecessor(Florigen)
Florigen.productions[p1] = Florigen.production_1

@dataclass
class PreFlorigen(Module):
    release: int
    def production_1(self):
        if self.release == 0:
            return Florigen()
        else:
            self.release -= 1
            return self

p1 = Predecessor(PreFlorigen)
PreFlorigen.productions[p1] = PreFlorigen.production_1

@dataclass
class UninhibitSignal(Module):
    def production_1(self):
        return None

p1 = Predecessor(UninhibitSignal)
UninhibitSignal.productions[p1] = UninhibitSignal.production_1


@dataclass
class Internode(Module):
    def production_1(self):
        return self, Florigen()
    def production_2(self):
        return UninhibitSignal(), self

    def draw(self):
        turtle.draw_internode_straight(6, 0.1)

p1 = Predecessor(Internode, [Florigen])
Internode.productions[p1] = Internode.production_1

p2 = Predecessor(Internode, right_context=[UninhibitSignal])
Internode.productions[p2] = Internode.production_2


@dataclass
class InhibitedInternode(Module):
    age: int
    def production_1(self):
        return PreFlorigen(self.age//4), Apex(2)
    def production_2(self):
        self.age += 1
        return self
    def draw(self):
        turtle.draw_internode_straight(2, 0.1)
    pass

p1 = Predecessor(InhibitedInternode, [UninhibitSignal, Internode])
InhibitedInternode.productions[p1] = InhibitedInternode.production_1
p2 = Predecessor(InhibitedInternode)
InhibitedInternode.productions[p2] = InhibitedInternode.production_2

@dataclass
class Leaf(Module):
    age: int
    def production_1(self):
        self.age += 1
        return self

    def draw(self):
        scale = self.age / 20 if self.age <20 else 1.0
        turtle.draw_object('Leaf', scale=scale)
    pass
p1 = Predecessor(Leaf)
Leaf.productions[p1] = Leaf.production_1


@dataclass
class Bud(Module):
    age: int
    def production_1(self):
        self.age += 1
        return self

    def draw(self):
        if self.age>= 10:
            turtle.draw_object('Flower')
        else:
            turtle.draw_object('FlowerBud')
    pass

p1 = Predecessor(Bud)
Bud.productions[p1] = Bud.production_1


@dataclass
class Apex(Module):
    divide: int

    def production_1(self):
        return UninhibitSignal(), Internode(), Bud(0)

    def production_2(self):
        if self.divide == 0:
            return Internode(), [RotateY(30), InhibitedInternode(0)], [RotateY(60), Leaf(0)], RotateZ(50), Apex(2)
        else:
            self.divide -= 1
            return self


p1 = Predecessor(Apex, [Florigen])
Apex.productions[p1] = Apex.production_1

p2 = Predecessor(Apex)
Apex.productions[p2] = Apex.production_2


##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################

lsys = Lsystem([PreFlorigen(20), Apex(0)])
lsys.derive(100)

# Need to execute in Blender!
import turtle
turtle.interpret(lsys.lstring, 'mycelis80')

# When running in Blender for creating models, you can comment these out, because Blender does not have
# networkx installed in its Python intepreter by default 
# from tree import *
# print(typeof(lsys.lstring))
# tree = eval(lsys.lstring)
# tree.show()



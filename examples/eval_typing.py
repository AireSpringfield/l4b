import sys
code_folder = r'F:\我的坚果云\编程语言\final\lpy'  # Change your code folder path!
sys.path.insert(0, code_folder)



from tree import *
from lstring import *

class A(Module):
    def __repr__(self):
        return 'A'
class B(Module):
    def __repr__(self):
        return 'B'
class C(Module):
    def __repr__(self):
        return 'C'
class D(Module):
    def __repr__(self):
        return 'D'
class E(Module):
    def __repr__(self):
        return 'E'

# Not in regular form - eval or typing will raise error
# lstring = [A(), [B()]]
# lstring = [A(), [[B()]], C()]

# type: Branch, not a Tree, cannot be shown
# lstring = [[A()], B()]

# type: Tree
lstring = [A(), [B(), [C()], D()], E()]


print(typeof(lstring))
tree = eval(lstring)
tree.show()
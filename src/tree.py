import networkx as nx
from lstring import *
from transform import *
import random
import matplotlib.pyplot as plt

class NoRulesApplied(Exception):
    def __init__(self, lstring):
        self.lstring = lstring

    def __str__(self):
        return 'No rules applied: {}'.format(str(self.lstring))

class SyntaxError(Exception):
    def __init__(self, lstring):
        self.lstring = lstring

    def __str__(self):
        return 'Syntax Error: {}'.format(str(self.lstring))



class Tree(object):
    def __init__(self, root):
        self.graph = nx.DiGraph()
        self.graph.add_node(root)
        self.root = root
        self.active = root

    def link(self, *childTrees):
        for childTree in childTrees:
            self.graph = nx.compose(self.graph, childTree.graph)
            self.graph.add_edge(self.active, childTree.root)

        self.active = childTrees[-1].active





    def show(self):
        def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):

            '''
            From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
            Licensed under Creative Commons Attribution-Share Alike

            If the graph is a tree this will return the positions to plot this in a
            hierarchical layout.

            G: the graph (must be a tree)

            root: the root node of current branch
            - if the tree is directed and this is not given,
              the root will be found and used
            - if the tree is directed and this is given, then
              the positions will be just for the descendants of this node.
            - if the tree is undirected and not given,
              then a random choice will be used.

            width: horizontal space allocated for this branch - avoids overlap with other branches

            vert_gap: gap between levels of hierarchy

            vert_loc: vertical location of root

            xcenter: horizontal location of root
            '''
            # https://stackoverflow.com/questions/29586520/can-one-get-hierarchical-graphs-from-networkx-with-python-3
            if not nx.is_tree(G):
                raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

            if root is None:
                if isinstance(G, nx.DiGraph):
                    root = next(iter(nx.topological_sort(G)))  # allows back compatibility with nx version 1.11
                else:
                    root = random.choice(list(G.nodes))

            def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
                '''
                see hierarchy_pos docstring for most arguments

                pos: a dict saying where all nodes go if they have been assigned
                parent: parent of this branch. - only affects it if non-directed

                '''

                if pos is None:
                    pos = {root: (xcenter, vert_loc)}
                else:
                    pos[root] = (xcenter, vert_loc)
                children = list(G.neighbors(root))
                if not isinstance(G, nx.DiGraph) and parent is not None:
                    children.remove(parent)
                if len(children) != 0:
                    dx = width / len(children)
                    nextx = xcenter - width / 2 - dx / 2
                    for child in children:
                        nextx += dx
                        pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                             vert_loc=vert_loc - vert_gap, xcenter=nextx,
                                             pos=pos, parent=root)
                return pos

            return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

        pos = hierarchy_pos(self.graph, self.root)
        nx.draw(self.graph, pos, with_labels=True, arrows=True)
        plt.show()


class Branch(object):
    branches = []

    def __init__(self, *trees):
        self.branches = []
        for tree in trees:
            self.branches.append(tree)

    def add(self, *trees):
        self.branches = list(trees) + self.branches


def isValue(t):
    if isinstance(t, Tree) or isinstance(t, Branch) or isinstance(t, Transform):
        return True
    if isinstance(t, list) and len(t) == 1 and isValue(t[0]):
        return True

    return False


def eval(lstring):
    t = tuple(lstring)
    while not isValue(t):
        t = eval1(t)
    return t

def eval1(t):
    if isinstance(t, Module):  # (E3)
        return Tree(t)
    elif isinstance(t, list):  # (E6)
        return [eval1(tuple(t))]
    elif isinstance(t, tuple):
        if len(t) == 0:
            raise SyntaxError(t)
        elif len(t) == 1:
            return eval1(t[0])
        elif len(t) == 2:
            t1 = t[0]
            t2 = t[1]
            if not isValue(t1):  # (E1)
                return eval1(t1), t2
            elif not isValue(t2):  # (E2)
                return t1, eval1(t2)
            else:
                if isinstance(t1, Tree) and isinstance(t2, Tree):  # (E4)
                    t1.link(t2)
                    return t1
                elif isinstance(t1, Tree) and isinstance(t2, Transform):  # (E5)
                    return t1
                elif isinstance(t2, Tree) and isinstance(t1, Transform):  # (E5')
                    return t2
                elif isinstance(t1, Branch) and isinstance(t2, Transform):  # (E5'')
                    return t1
                elif isinstance(t2, Branch) and isinstance(t1, Transform):  # (E5''')
                    return t2
                elif isinstance(t1, list) and isinstance(t1[0], Tree) and isinstance(t2, Tree):  # (E7)
                    return Branch(t1[0], t2)
                elif isinstance(t1, list) and isinstance(t1[0], Tree) and isinstance(t2, Branch):  # (E8)
                    t2.add(t1[0])
                    return t2
                elif isinstance(t1, Tree) and isinstance(t2, Branch):
                    t1.link(*t2.branches)
                    return t1
                else:
                    raise NoRulesApplied(t)
        else:
            if not isValue(t[0]):  # (E1)
                return (eval1(t[0]),) + t[1:]

            else:  # (E2)
                tt2 = eval1(t[1:])
                if isinstance(tt2, tuple):
                    return (t[0],) + tt2
                else:
                    return t[0], tt2

    else:
        raise NoRulesApplied(t)


def _typeof(t):
    if isinstance(t, Tree):  # (T1)
        return Tree
    elif isinstance(t, Module):  # (T2)
        return Tree
    elif isinstance(t, Branch):  # (T3)
        return Branch
    elif isinstance(t, Transform):  # (T4)
        return Transform
    elif isinstance(t, list):
        return [_typeof(tuple(t))]
    elif isinstance(t, tuple) and len(t) == 1:
        return _typeof(t[0])
    elif isinstance(t, tuple) and len(t) >= 2:
        t1 = t[0]
        T1 = _typeof(t1)
        t2 = t[1] if len(t) == 2 else tuple(t[1:])
        T2 = _typeof(t2)
        if T1 == Tree and T2 == Tree:  # (T5)
            return Tree
        elif T1 == Tree and T2 == Transform:  # (T6)
            return Tree
        elif T2 == Tree and T1 == Transform:  # (T6')
            return Tree
        elif T1 == Branch and T2 == Transform:  # (T6'')
            return Branch
        elif T2 == Branch and T1 == Transform:  # (T6''')
            return Branch
        elif T1 == [Tree] and T2 == Tree:  # (T7)
            return Branch
        elif T1 == [Tree] and T2 == Branch:  # (T8)
            return Branch
        elif T1 == Tree and T2 == Branch:  # (T9)
            return Tree
        else:
            raise NoRulesApplied(t)
    else:
        raise NoRulesApplied(t)

def typeof(lstring):
    return _typeof(tuple(lstring))


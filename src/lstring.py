from collections import OrderedDict


def nested_map(nested_list, map_fun, **kwargs):
    try:
        kwargs['complete']
    except KeyError:
        kwargs['complete'] = nested_list.copy()

    try:
        index = kwargs['index']
    except KeyError:
        index = []


    new_list = nested_list.copy()

    for i in range(len(nested_list)):
        item = nested_list[i]
        new_index = index.copy()
        new_index.append(i)
        kwargs['index'] = new_index

        if isinstance(item, list):
            new_list[i] = nested_map(item, map_fun, **kwargs)
        else:
            new_list[i] = map_fun(item, **kwargs)

    kwargs['index'] = index
    return new_list

def nested_reduce(nested_list, reduce_fun, init_result, **kwargs):
    try:
        index = kwargs['index']
    except KeyError:
        index = []

    result = init_result
    for i in range(len(nested_list)):
        item = nested_list[i]
        new_index = index.copy()
        new_index.append(i)
        kwargs['index'] = new_index

        if isinstance(item, list):
            result = reduce_fun(nested_reduce(item, reduce_fun, init_result), result, **kwargs)
        else:
            result = reduce_fun(item, result, **kwargs)

    kwargs['index'] = index
    return result


def at(nested_list, index:list):
    m = nested_list
    for i in index:
        m = m[i]
    return m



class Predecessor(object):
    strict = None
    left_context = []
    right_context = []
    # ignores = []

    def __init__(self, strict, left_context = [], right_context = []):
        self.strict = strict
        self.left_context = left_context
        self.right_context = right_context


    def __str__(self):
        left = nested_map(self.left_context, lambda module_type: module_type.__name__)if len(self.left_context) != 0 else ''
        right = nested_map(self.right_context, lambda module_type: module_type.__name__) if len(self.right_context) != 0 else ''
        left = nested_reduce(left, '', lambda a,b : a+b)
        right = nested_reduce(right, '', lambda a,b : a+b)
        return left  + '|' + self.strict.__name__ + '|' + right


class MetaModule(type):
    def __new__(cls, name, bases, attrs):
        attrs['productions'] = OrderedDict() # each Module Class gets its own productions
        # cls.productions = OrderedDict()
        return type.__new__(cls, name, bases, attrs)


class Module(object, metaclass=MetaModule):

    # def __str__(self):
    #     return self.__name__

    def __hash__(self):
        return id(self)

    def apply(self, predecessor:Predecessor):
        try:
            return self.productions[predecessor](self)
        except KeyError as e:
            raise NoProductionMatched(type(self) , e.args[0])

    def draw(self):
        pass




class NoProductionMatched(KeyError):
    def __init__(self, module_type:Module, predecessor: Predecessor):
        self.module_type = module_type
        self.predecessor = predecessor

    def __str__(self):
        return 'Module {} has no production with predecessor {}'.format(self.module_type.__name__, str(self.predecessor))


def Eval(nested_list):


    return

def Typing(nested_list):


    return

















# def render_tree(root: Node):
#     '''
#     >> > for pre, _, node in RenderTree(root):
#         ...
#         print("%s%s" % (pre, node.name))
#     root
#     ├── sub0
#     │   ├── sub0B
#     │   └── sub0A
#     └── sub1
#     '''
#     pass













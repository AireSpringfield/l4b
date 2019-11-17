from lstring import *
from transform import *

using_typechecker = False  # Set False when using in Blender 

if using_typechecker:
    from tree import typeof



def _check_left(lstr:list, index_strict:list, pattern:list)-> bool:
    if len(pattern) == 0:
        return True

    def move_left(index: list):
        idx = index.copy()
        i = idx.pop()
        if i == 0:  # Move out of a branch
            if len(idx) == 0:  # Left-most already
                return None
            else:  # Could either be a module or a branch
                idx[-1] -= 1
                return idx
        else:  # A module in the branch
            idx.append(i-1)
            return idx  # Left could be either a branch or a module



    # The first module to compare is the one left to strict
    index_module = move_left(index_strict.copy())
    # Find the index of the first pattern to compare
    index_pattern = [len(pattern) - 1]

    matched = True
    while matched is True:
        if index_pattern is None:  # Pattern exhausts, matching is successful
            break
        if index_module is None:  # Module exhausts, matching is failed
            matched = False
            break

        m = at(lstr, index_module)
        p = at(pattern, index_pattern)

        ####################################################################################################
        # Branching situation handling

        if isinstance(m, list):  # Skip branches in L-string
            index_module = move_left(index_module)
            continue

        ####################################################################################################
        # Comparison
        if isinstance(m, Transform):  # TODO: ignore
            index_module = move_left(index_module)
            continue

        if not isinstance(m, p):  # Not matched
            matched = False
            break

        # Matched. Compare next pair.
        index_module = move_left(index_module)
        index_pattern = move_left(index_pattern)

    return matched


def _check_right(lstr: list, index_strict: list, pattern: list) -> bool:
    if len(pattern) == 0:
        return True

    def move_right(index: list, nested_list: list): #fixme
        idx = index.copy()
        i = idx.pop()
        size = len(at(nested_list, idx))
        if i == size - 1:  # Move out of a branch
            bExitBranch = True
            if len(idx) == 0:  # Right-most already
                return None, bExitBranch
            else:  # Could either be a module or a branch
                idx[-1] += 1
                return idx, bExitBranch
        else:  # A module in the branch
            bExitBranch = False
            idx.append(i+1)
            return idx, bExitBranch  # Right could be either a branch or a module

    def skip_current_branch(index:list, nested_list: list):
        idx = index.copy()
        idx.pop()
        if len(idx) == 0:
            return None
        idx, bExitBranch = move_right(idx, nested_list)  # Note: bExitBranch must be False
        return idx

    # The index of first module to compare
    index_module, module_exit_branch = move_right(index_strict.copy(), lstr)
    # Find the index of the first pattern to compare
    index_pattern = [0]
    p = pattern[0]
    pattern_exit_branch = False

    matched = True
    while matched is True:
        if index_pattern is None:  # Pattern exhausts, matching is successful
            break
        if index_module is None:  # Module exhausts, matching is failed
            matched = False
            break

        if pattern_exit_branch and not module_exit_branch: # Skip the current L-string branch
            index_module = skip_current_branch(index_module, lstr)
            module_exit_branch = True
            continue

        if not pattern_exit_branch and module_exit_branch: # This branch pattern matching failed. Try next branch in L-string
            index_pattern.pop()  # Recompare the branch pattern. If index_pattern is empty, in next iteration p will be the whole right context
            # We do not know whether the two flags are correct by now - only let them coincide and enter the following process
            pattern_exit_branch = module_exit_branch
            continue

        # If pattern_exit_branch and module_exit_branch are the same, just execute the following

        m = at(lstr, index_module)
        p = at(pattern, index_pattern)
        
        if isinstance(m, list) and isinstance(p, list):  # m and p are both branches: compare inside
            index_module.append(0)
            index_pattern.append(0)
            continue

        if isinstance(m, list) and not isinstance(p, list):  # m is a branch and p is a module: skip the branch
            index_module, module_exit_branch = move_right(index_module, lstr) 
            # By regular form, module_exit_branch must be False now
            # Let the two flags coincide
            pattern_exit_branch = module_exit_branch
            continue

        if not isinstance(m, list) and isinstance(p, list):  # m is a module and p is a branch: fail
            matched = False
            break

        # m is a module and p is a module: comparison
        # TODO: ignore
        if isinstance(m, Transform):
            index_module, module_exit_branch = move_right(index_module, lstr)
            continue

        if not isinstance(m, p):  # Not matched
            matched = False
            break

        # Matched. Compare next pair.
        index_module, module_exit_branch = move_right(index_module, lstr)
        index_pattern, pattern_exit_branch = move_right(index_pattern, pattern)


    return matched


def _apply_production(module: Module, **kwargs):
    module_type = type(module)
    if module_type == Transform:
        return module

    complete_lstr = kwargs['complete']
    index = kwargs['index']
    # TODO: ignore
    if isinstance(module, Transform):
        return module
    predecessors = list(module_type.productions.keys())
    bFound = False
    for predecessor in predecessors:
        matched = True
        # Make sure that the L-string is in normal form
        if using_typechecker:
            assert typeof(complete_lstr) == Tree
        # Check left context
        matched &= _check_left(complete_lstr, index, predecessor.left_context)
        # Check right context
        matched &= _check_right(complete_lstr, index, predecessor.right_context)

        if matched == True:
            bFound = True
            break

    if bFound:
        return module.apply(predecessor)
    else:
        return module



def _solve_tuples(nested_list: list):
    new_list = []
    for item in nested_list:
        if item is None:
            continue
        elif isinstance(item, list):
            new_list.append(_solve_tuples(item))
        elif isinstance(item, tuple):
            new_list.extend(item)
        else:
            new_list.append(item)
    return new_list





class Lsystem(object):
    lstring:list = []

    def __init__(self, lstring):
        self.lstring = lstring




    def derive(self, nSteps):
        # Make sure that the axiom is in normal form
        if using_typechecker:
            assert typeof(self.lstring) == Tree
        for n in range(nSteps):
            self.lstring = _solve_tuples(nested_map(self.lstring, _apply_production))
        return




        return

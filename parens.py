# retrieved from http://www.python-forum.org/pythonforum/viewtopic.php?f=14&t=5842#p25801
# on 24-Jun-2011

# inspired by http://python-forum.org/py/viewtopic.php?t=5842

# we will use a high-performance deque object; we could use a list instead.
import collections

# create left to right parenthesis mappings
lrmap = {"(":")", "[":"]", "{":"}"}

# derive sets of left and right parentheses
lparens = set(lrmap.iterkeys())
rparens = set(lrmap.itervalues())

def checkParentheses(string):
    '''Check that all parentheses in a string come in matched nested pairs.'''
    parenstack = collections.deque()
    for ch in string:
        if ch in lparens:
            parenstack.append(ch)
        elif ch in rparens:
            try:
                if lrmap[parenstack.pop()] != ch:
                    # wrong type of parenthesis popped from stack
                    return False
            except IndexError:
                # no opening parenthesis left in stack
                return False
    # if we are not out of opening parentheses, we have a mismatch
    return not parenstack



if __name__ == "__main__":
    strings = ["abcdefgh", "ab(cdef)gh", "ab(c[de]f)gh", "ab(cdefgh",
       "ab(c[def)g]h"]
    for string in strings:
        print checkParentheses(string)
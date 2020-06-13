{% import 'main.py' as main with context %}
# This file was autogenerated by uvm-python-rdl
from uvm import *
import itertools

def create_array(*args):
    if len(args) == 1:
        return None
    res = []
    ndim = args[0]
    rest = args[1:]
    for n in range(ndim):
        res.append(create_array(*rest))
    return res

{{ main.top()}}

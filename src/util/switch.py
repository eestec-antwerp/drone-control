# Simple switch class
# Taken from SmartHome, ask Evert Heylen

from functools import wraps
import types

def case(*list_what):
    def decorator(function):
        function.__cases__ = list_what
        return function
    return decorator

# not a decorator
def classitems(dct, bases):
    for b in bases:
        yield from classitems(b.__dict__, b.__bases__)
    yield from dct.items()

def create_meta(_func):
    def f(func=_func):
        class MetaSwitch(type):
            __call__ = func
        return MetaSwitch
    return f()
            

class MetaSwitch(type):
    def __new__(self, name, bases, dct):
        dispatch = {}
        full_dct = {}
        for (k,v) in classitems(dct, bases):
            full_dct[k] = v
            
        def select(arg, *args, **kwargs):
            return arg
        
        def default(*args, **kwargs):
            pass
        
        for (k,f) in classitems(dct, bases):
            if hasattr(f, "__cases__"):
                for c in f.__cases__:
                    dispatch[c] = f
    
        select = full_dct.get("select", select)
        default = full_dct.get("default", default)
        
        dct["select"] = select
        dct["default"] = default
        dct["dispatch"] = dispatch
        
        return type.__new__(self, name, bases, dct)
    
    def __call__(cls, *args, **kwargs):
        key = cls.select(*args, **kwargs)
        if key in cls.dispatch:
            return cls.dispatch[key](*args, **kwargs)
        else:
            return cls.default(*args, **kwargs)

class switch(metaclass=MetaSwitch):
    # Clients don't need to know it uses metaclasses
    pass

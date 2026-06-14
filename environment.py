"""
This file is basically:

JavaScript Variable Memory
(variables & scopes)
"""
class Environment:
    def __init__(self, outer=None):
        self.store = {}        # Maps variable name -> value
        self.consts = set()     # Set of const variable names
        self.outer = outer      # Outer/parent Environment

    def declare(self, name, value, is_const=False):
        # In JS, redeclaring in the same scope with let/const is a syntax error,
        # but for simplicity we will just overwrite or raise if we want.
        # Redeclaring standard variables might happen if user code does it, 
        # but let's throw an error to be safe and clean, or just overwrite if it's the global scope/var.
        # Actually, let's just write to store.
        self.store[name] = value
        if is_const:
            self.consts.add(name)

    def get(self, name):
        if name in self.store:
            return self.store[name]
        if self.outer:
            return self.outer.get(name)
        raise NameError(f"ReferenceError: {name} is not defined")

    def set(self, name, value):
        # We need to find where it is declared and modify it there
        if name in self.store:
            if name in self.consts:
                raise TypeError(f"TypeError: Assignment to constant variable '{name}'")
            self.store[name] = value
            return value
            
        if self.outer:
            return self.outer.set(name, value)
            
        raise NameError(f"ReferenceError: {name} is not defined")
"""
(JS behavior)
"""
import math
import random
import datetime
from parser_ast import Undefined

# 1. Type Coercion Helpers

def js_to_string(val):
    if val is None:
        return "null"
    if val is Undefined:
        return "undefined"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, JSArray):
        return val.get_method('join')()
    if isinstance(val, JSObject):
        return "[object Object]"
    if isinstance(val, float):
        if math.isnan(val):
            return "NaN"
        if math.isinf(val):
            return "Infinity" if val > 0 else "-Infinity"
        if val.is_integer():
            return str(int(val))
        return str(val)
    return str(val)

def js_to_number(val):
    if val is None:
        return 0
    if val is Undefined:
        return float('nan')
    if isinstance(val, bool):
        return 1 if val else 0
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        val_s = val.strip()
        if not val_s:
            return 0
        try:
            return float(val_s) if '.' in val_s or 'e' in val_s.lower() else int(val_s)
        except ValueError:
            return float('nan')
    # Objects / Arrays
    val_prim = js_to_primitive(val)
    if isinstance(val_prim, (JSArray, JSObject)):
        return float('nan')
    return js_to_number(val_prim)

def js_is_truthy(val):
    if val is None or val is Undefined:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        if val == 0 or (isinstance(val, float) and math.isnan(val)):
            return False
        return True
    if isinstance(val, str):
        return len(val) > 0
    return True # objects, arrays are truthy

def js_to_primitive(val):
    if isinstance(val, JSArray):
        return val.get_method('join')()
    if isinstance(val, JSObject):
        return "[object Object]"
    return val

# Strict Equality (===)
def js_strict_eq(a, b):
    if type(a) != type(b):
        # undefined and null are different types under ===
        # but wait, if one is float and other is int, in JS they are both "number" type.
        # So in Python, we should check if they are both numbers (int or float).
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            pass
        else:
            return False
            
    if a is Undefined or b is Undefined:
        return a is Undefined and b is Undefined
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, (JSArray, JSObject, JSDate)):
        return a is b
        
    # float nan checks
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if math.isnan(a) or math.isnan(b):
            return False
            
    return a == b

# Loose Equality (==)
def js_loose_eq(a, b):
    if (a is None or a is Undefined) and (b is None or b is Undefined):
        return True
    if (a is None or a is Undefined) or (b is None or b is Undefined):
        return False
        
    # If same base types
    if type(a) == type(b) or (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        return js_strict_eq(a, b)
        
    # Coercions
    # Number and String
    if isinstance(a, (int, float)) and isinstance(b, str):
        return js_strict_eq(a, js_to_number(b))
    if isinstance(a, str) and isinstance(b, (int, float)):
        return js_strict_eq(js_to_number(a), b)
        
    # Boolean with anything
    if isinstance(a, bool):
        return js_loose_eq(js_to_number(a), b)
    if isinstance(b, bool):
        return js_loose_eq(a, js_to_number(b))
        
    # Object/Array with Primitive
    if isinstance(a, (JSArray, JSObject)) and isinstance(b, (str, int, float, bool)):
        return js_loose_eq(js_to_primitive(a), b)
    if isinstance(b, (JSArray, JSObject)) and isinstance(a, (str, int, float, bool)):
        return js_loose_eq(a, js_to_primitive(b))
        
    return False

def js_add(a, b):
    # If either is string (or represents string/object after primitive coercion)
    # JS first converts to primitives
    a_prim = js_to_primitive(a)
    b_prim = js_to_primitive(b)
    if isinstance(a_prim, str) or isinstance(b_prim, str):
        return js_to_string(a_prim) + js_to_string(b_prim)
    return js_to_number(a_prim) + js_to_number(b_prim)

def js_lt(a, b):
    a_prim = js_to_primitive(a)
    b_prim = js_to_primitive(b)
    if isinstance(a_prim, str) and isinstance(b_prim, str):
        return a_prim < b_prim
    return js_to_number(a_prim) < js_to_number(b_prim)

def js_le(a, b):
    a_prim = js_to_primitive(a)
    b_prim = js_to_primitive(b)
    if isinstance(a_prim, str) and isinstance(b_prim, str):
        return a_prim <= b_prim
    return js_to_number(a_prim) <= js_to_number(b_prim)

def js_gt(a, b):
    a_prim = js_to_primitive(a)
    b_prim = js_to_primitive(b)
    if isinstance(a_prim, str) and isinstance(b_prim, str):
        return a_prim > b_prim
    return js_to_number(a_prim) > js_to_number(b_prim)

def js_ge(a, b):
    a_prim = js_to_primitive(a)
    b_prim = js_to_primitive(b)
    if isinstance(a_prim, str) and isinstance(b_prim, str):
        return a_prim >= b_prim
    return js_to_number(a_prim) >= js_to_number(b_prim)


# 2. JS Object & Reference Types

class JSObject:
    def __init__(self, properties=None):
        self.properties = {}
        if properties:
            for k, v in properties.items():
                self.properties[str(k)] = v

    def get_prop(self, name):
        name = str(name)
        if name in self.properties:
            return self.properties[name]
        return Undefined

    def set_prop(self, name, value):
        self.properties[str(name)] = value
        return value

    def __repr__(self):
        props = ", ".join(f"{k}: {repr(v)}" for k, v in self.properties.items())
        return f"{{ {props} }}"


class JSArray:
    def __init__(self, elements=None):
        self.elements = list(elements) if elements is not None else []

    def get_item(self, idx):
        try:
            # Check float/int index
            i = int(idx)
            # Negative index in JS bracket notation is not native array index (it behaves like object property)
            if i < 0 or i >= len(self.elements):
                # check dict
                return self.__dict__.get(str(idx), Undefined)
            return self.elements[i]
        except (ValueError, TypeError):
            # Try to get custom attribute
            return self.__dict__.get(str(idx), Undefined)

    def set_item(self, idx, value):
        try:
            i = int(idx)
            if i < 0:
                # set as property
                self.__dict__[str(idx)] = value
                return value
            if i >= len(self.elements):
                # pad array with undefined
                self.elements.extend([Undefined] * (i - len(self.elements) + 1))
            self.elements[i] = value
            return value
        except (ValueError, TypeError):
            self.__dict__[str(idx)] = value
            return value

    def get_method(self, name, evaluator=None):
        name = str(name)
        if name == 'length':
            return len(self.elements)

        # Standard JS Array methods
        if name == 'push':
            return lambda *args: (self.elements.extend(args) or len(self.elements))
        if name == 'pop':
            return lambda: self.elements.pop() if self.elements else Undefined
        if name == 'shift':
            return lambda: self.elements.pop(0) if self.elements else Undefined
        if name == 'unshift':
            def unshift(*args):
                self.elements = list(args) + self.elements
                return len(self.elements)
            return unshift
        if name == 'slice':
            def slice_fn(start=None, end=None):
                s = int(js_to_number(start)) if start is not None else 0
                e = int(js_to_number(end)) if end is not None else len(self.elements)
                # handle negative slice indices
                if s < 0: s = max(len(self.elements) + s, 0)
                if e < 0: e = max(len(self.elements) + e, 0)
                return JSArray(self.elements[s:e])
            return slice_fn
        if name == 'splice':
            def splice_fn(start, delete_count=None, *items):
                s = int(js_to_number(start))
                if s < 0:
                    s = max(len(self.elements) + s, 0)
                else:
                    s = min(s, len(self.elements))
                
                dc = int(js_to_number(delete_count)) if delete_count is not None else (len(self.elements) - s)
                dc = max(0, min(dc, len(self.elements) - s))
                
                deleted = self.elements[s:s+dc]
                self.elements[s:s+dc] = list(items)
                return JSArray(deleted)
            return splice_fn
        if name == 'concat':
            def concat_fn(*args):
                res = list(self.elements)
                for arg in args:
                    if isinstance(arg, JSArray):
                        res.extend(arg.elements)
                    else:
                        res.append(arg)
                return JSArray(res)
            return concat_fn
        if name == 'includes':
            return lambda x: any(js_strict_eq(el, x) for el in self.elements)
        if name == 'indexOf':
            def index_of(x, from_index=0):
                f = int(js_to_number(from_index))
                if f < 0: f = max(len(self.elements) + f, 0)
                for i in range(f, len(self.elements)):
                    if js_strict_eq(self.elements[i], x):
                        return i
                return -1
            return index_of
        if name == 'join':
            def join_fn(sep=','):
                # JS join treats undefined and null as empty strings
                def to_join_str(el):
                    if el is None or el is Undefined:
                        return ""
                    return js_to_string(el)
                return sep.join(to_join_str(el) for el in self.elements)
            return join_fn
        if name == 'sort':
            def sort_fn(compare_fn=None):
                if compare_fn is None:
                    # Sort by converting to string
                    self.elements.sort(key=js_to_string)
                else:
                    from functools import cmp_to_key
                    def wrapped_cmp(a, b):
                        res = evaluator.call_function(compare_fn, [a, b])
                        return int(js_to_number(res))
                    self.elements.sort(key=cmp_to_key(wrapped_cmp))
                return self
            return sort_fn
        if name == 'reverse':
            def reverse_fn():
                self.elements.reverse()
                return self
            return reverse_fn

        # High order methods
        if name == 'map':
            def map_fn(callback):
                res = []
                for i, el in enumerate(self.elements):
                    res.append(evaluator.call_function(callback, [el, i, self]))
                return JSArray(res)
            return map_fn
        if name == 'filter':
            def filter_fn(callback):
                res = []
                for i, el in enumerate(self.elements):
                    if js_is_truthy(evaluator.call_function(callback, [el, i, self])):
                        res.append(el)
                return JSArray(res)
            return filter_fn
        if name == 'reduce':
            def reduce_fn(callback, initial_value=Undefined):
                if not self.elements and initial_value is Undefined:
                    raise TypeError("TypeError: Reduce of empty array with no initial value")
                start_idx = 0
                acc = initial_value
                if acc is Undefined:
                    acc = self.elements[0]
                    start_idx = 1
                for i in range(start_idx, len(self.elements)):
                    acc = evaluator.call_function(callback, [acc, self.elements[i], i, self])
                return acc
            return reduce_fn
        if name == 'find':
            def find_fn(callback):
                for i, el in enumerate(self.elements):
                    if js_is_truthy(evaluator.call_function(callback, [el, i, self])):
                        return el
                return Undefined
            return find_fn
        if name == 'some':
            def some_fn(callback):
                for i, el in enumerate(self.elements):
                    if js_is_truthy(evaluator.call_function(callback, [el, i, self])):
                        return True
                return False
            return some_fn
        if name == 'every':
            def every_fn(callback):
                for i, el in enumerate(self.elements):
                    if not js_is_truthy(evaluator.call_function(callback, [el, i, self])):
                        return False
                return True
            return every_fn

        # Property access fallback
        if name in self.__dict__:
            return self.__dict__[name]
        return Undefined

    def __repr__(self):
        return f"[{', '.join(js_to_string(el) if isinstance(el, str) else repr(el) for el in self.elements)}]"


# String methods dynamic helper (to avoid wrapping primitive str)
def get_string_member(s, name):
    name = str(name)
    if name == 'length':
        return len(s)
        
    if name == 'split':
        def split_fn(sep=None):
            # JS split behaviour:
            # split("") splits by characters.
            # split() returns array with full string.
            if sep is None:
                return JSArray([s])
            if sep == "":
                return JSArray(list(s))
            return JSArray(s.split(sep))
        return split_fn
    if name == 'slice':
        def slice_fn(start, end=None):
            st = int(js_to_number(start))
            en = int(js_to_number(end)) if end is not None else len(s)
            if st < 0: st = max(len(s) + st, 0)
            if en < 0: en = max(len(s) + en, 0)
            return s[st:en]
        return slice_fn
    if name == 'substring':
        def substring_fn(start, end=None):
            st = max(0, int(js_to_number(start)))
            en = max(0, int(js_to_number(end))) if end is not None else len(s)
            # JS swap if start > end
            if st > en:
                st, en = en, st
            return s[st:en]
        return substring_fn
    if name == 'trim':
        return lambda: s.strip()
    if name == 'toUpperCase':
        return lambda: s.upper()
    if name == 'toLowerCase':
        return lambda: s.lower()
    if name == 'includes':
        return lambda search, start=0: search in s[int(js_to_number(start)):]
    if name == 'startsWith':
        return lambda search, pos=0: s.startswith(search, int(js_to_number(pos)))
    if name == 'endsWith':
        def ends_with(search, length=None):
            l = int(js_to_number(length)) if length is not None else len(s)
            l = min(max(0, l), len(s))
            return s[:l].endswith(search)
        return ends_with
    if name == 'indexOf':
        return lambda search, start=0: s.find(search, int(js_to_number(start)))
    if name == 'replace':
        return lambda search, rep: s.replace(search, rep, 1)
    if name == 'replaceAll':
        return lambda search, rep: s.replace(search, rep)
        
    return Undefined


class JSDate:
    def __init__(self, *args):
        if not args:
            self.dt = datetime.datetime.now()
        elif len(args) == 1:
            try:
                ms = int(js_to_number(args[0]))
                self.dt = datetime.datetime.fromtimestamp(ms / 1000.0)
            except (ValueError, TypeError):
                self.dt = datetime.datetime.now()
        else:
            y = int(js_to_number(args[0]))
            m = int(js_to_number(args[1])) + 1 # JS 0-11 to Python 1-12
            d = int(js_to_number(args[2])) if len(args) > 2 else 1
            h = int(js_to_number(args[3])) if len(args) > 3 else 0
            mi = int(js_to_number(args[4])) if len(args) > 4 else 0
            se = int(js_to_number(args[5])) if len(args) > 5 else 0
            ms = int(js_to_number(args[6])) if len(args) > 6 else 0
            self.dt = datetime.datetime(y, m, d, h, mi, se, ms * 1000)

    def get_method(self, name):
        name = str(name)
        if name == 'getTime':
            return lambda: self.dt.timestamp() * 1000
        if name == 'getFullYear':
            return lambda: self.dt.year
        if name == 'getMonth':
            return lambda: self.dt.month - 1
        if name == 'getDate':
            return lambda: self.dt.day
        if name == 'getDay':
            return lambda: (self.dt.weekday() + 1) % 7
        if name == 'getHours':
            return lambda: self.dt.hour
        if name == 'getMinutes':
            return lambda: self.dt.minute
        if name == 'getSeconds':
            return lambda: self.dt.second
        if name == 'getMilliseconds':
            return lambda: self.dt.microsecond // 1000
        if name == 'toISOString':
            return lambda: self.dt.isoformat()
        if name == 'toString':
            return lambda: self.dt.strftime("%a %b %d %Y %H:%M:%S GMT")
            
        raise AttributeError(f"JSDate has no attribute {name}")


class JSMath:
    def __init__(self):
        self.E = math.e
        self.LN2 = math.log(2)
        self.LN10 = math.log(10)
        self.LOG2E = math.log2(math.e)
        self.LOG10E = math.log10(math.e)
        self.PI = math.pi
        self.SQRT1_2 = math.sqrt(0.5)
        self.SQRT2 = math.sqrt(2)

    def floor(self, x):
        return math.floor(js_to_number(x))

    def random(self):
        return random.random()

    def abs(self, x):
        return abs(js_to_number(x))

    def ceil(self, x):
        return math.ceil(js_to_number(x))

    def round(self, x):
        num = js_to_number(x)
        return math.floor(num + 0.5)

    def max(self, *args):
        if not args:
            return float('-inf')
        return max(js_to_number(x) for x in args)

    def min(self, *args):
        if not args:
            return float('inf')
        return min(js_to_number(x) for x in args)

    def pow(self, x, y):
        return js_to_number(x) ** js_to_number(y)

    def sqrt(self, x):
        return math.sqrt(js_to_number(x))
        
    def get_method(self, name):
        name = str(name)
        if hasattr(self, name):
            attr = getattr(self, name)
            if callable(attr):
                return attr
            return attr
        raise AttributeError(f"Math has no property {name}")

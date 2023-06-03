#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper, wraps
import traceback




def disable(func):
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable
    '''
    return func if callable(func) else lambda func: func


def decorator(func_decorator):
    '''
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    '''
    def inner_deco(func):
        return update_wrapper(func_decorator, func)
    return inner_deco


def countcalls(func):
    '''Decorator that counts calls made to the function decorated.'''
    @wraps(func)
    def inner_countcalls(*args, **kwargs):
        inner_countcalls.calls += 1
        return func(*args, **kwargs)
    inner_countcalls.calls = 0
    return inner_countcalls


def memo(func):
    '''
    Memoize a function so that it caches all return values for
    faster future lookups.
    '''
    cache_dict = dict()
    @wraps(func)
    def inner_memo(*args):
        key_args = args
        if key_args not in cache_dict.keys():
            cache_dict[key_args] = func(*args)
        return cache_dict[key_args]

    return inner_memo


def n_ary(func):
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''
    @wraps(func)
    def inner_n_ary(x, *args):
        if not args:
            return x
        else:
            result = x
            for item in args:
                result = func(result, item)
            return result

    return inner_n_ary


def trace(fill_value):
    '''Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    '''
    def trace_decorator(f):
        @wraps(f)
        def wrapper(*args):
            prefix = fill_value * wrapper.level
            fargs = ", ".join(str(a) for a in args)
            print (f"{prefix} --> {f.__name__}({fargs})")
            wrapper.level += 1
            result = f(*args)
            print ("{} <-- {}({}) == {}".format(prefix, f.__name__, fargs, result))
            wrapper.level -= 1
            return result
        wrapper.level = 0
        return wrapper
    return trace_decorator


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print(foo(4, 3))
    print(foo(4, 3, 2))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    print(bar(4, 3, 2))
    print(bar(4, 3, 2, 1))
    print("bar was called", bar.calls, "times")

    print(fib.__doc__)
    fib(3)
    print(fib.calls, 'calls made')


if __name__ == '__main__':
    main()

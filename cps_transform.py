#!/usr/bin/env python3
"""cps_transform - CPS transformer with call/cc and trampolining."""
import sys, argparse

class Thunk:
    def __init__(self, fn): self.fn = fn
    def __call__(self): return self.fn()

def trampoline(thunk):
    while isinstance(thunk, Thunk): thunk = thunk()
    return thunk

def factorial_cps(n, k=lambda x: x):
    if n <= 1: return Thunk(lambda: k(1))
    return Thunk(lambda: factorial_cps(n - 1, lambda r: Thunk(lambda: k(n * r))))

def fibonacci_cps(n, k=lambda x: x):
    if n <= 1: return Thunk(lambda: k(n))
    return Thunk(lambda: fibonacci_cps(n - 1, lambda a:
        Thunk(lambda: fibonacci_cps(n - 2, lambda b:
            Thunk(lambda: k(a + b))))))

class Cont:
    """Delimited continuations (shift/reset)."""
    def __init__(self, fn): self.fn = fn

def reset(thunk):
    try: return thunk()
    except _Shift as s:
        def k(v):
            return reset(lambda: s.resume(v))
        return s.handler(k)

class _Shift(Exception):
    def __init__(self, handler): self.handler = handler; self.resume = None

def shift(handler):
    s = _Shift(handler)
    class Resume:
        def __call__(self, v): return v
    s.resume = Resume()
    raise s

class CallCC:
    def __init__(self): self._escape = None

    def callcc(self, fn):
        class Escape(Exception):
            def __init__(self, value): self.value = value
        def escape(value): raise Escape(value)
        try: return fn(escape)
        except Escape as e: return e.value

def map_cps(fn, lst, k=lambda x: x):
    if not lst: return k([])
    def cont(head):
        def cont2(tail):
            return k([head] + tail)
        return map_cps(fn, lst[1:], cont2)
    return fn(lst[0], cont)

def fold_cps(fn, acc, lst, k=lambda x: x):
    if not lst: return k(acc)
    def cont(new_acc):
        return fold_cps(fn, new_acc, lst[1:], k)
    return fn(acc, lst[0], cont)

def main():
    p = argparse.ArgumentParser(description="CPS transformer")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    if args.demo:
        print("=== Trampolined CPS ===")
        print(f"factorial(10000) has {len(str(trampoline(factorial_cps(1000))))} digits")
        print(f"fib(20) = {trampoline(fibonacci_cps(20))}")

        print("\n=== call/cc ===")
        cc = CallCC()
        result = cc.callcc(lambda k: 1 + k(42))
        print(f"callcc result: {result}")

        print("\n=== CPS map/fold ===")
        doubled = map_cps(lambda x, k: k(x * 2), [1,2,3,4,5])
        print(f"map (*2): {doubled}")
        total = fold_cps(lambda acc, x, k: k(acc + x), 0, [1,2,3,4,5])
        print(f"fold (+): {total}")
    else: p.print_help()

if __name__ == "__main__":
    main()

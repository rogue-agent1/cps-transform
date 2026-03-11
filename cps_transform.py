#!/usr/bin/env python3
"""cps_transform - Continuation-Passing Style transformation for a simple functional language.

Usage: python cps_transform.py [--demo]
"""
import sys

# Direct-style AST
class Var:
    def __init__(self, n): self.n = n
    def __repr__(self): return self.n
class Num:
    def __init__(self, v): self.v = v
    def __repr__(self): return str(self.v)
class Lam:
    def __init__(self, p, b): self.p = p; self.b = b
    def __repr__(self): return f"(λ{self.p}. {self.b})"
class App:
    def __init__(self, f, a): self.f = f; self.a = a
    def __repr__(self): return f"({self.f} {self.a})"
class BinOp:
    def __init__(self, op, l, r): self.op = op; self.l = l; self.r = r
    def __repr__(self): return f"({self.l} {self.op} {self.r})"
class IfZ:
    def __init__(self, c, t, e): self.c = c; self.t = t; self.e = e
    def __repr__(self): return f"(if0 {self.c} {self.t} {self.e})"

# CPS AST
class CLam:
    def __init__(self, ps, b): self.ps = ps; self.b = b
    def __repr__(self): return f"(λ({','.join(self.ps)}). {self.b})"
class CApp:
    def __init__(self, f, args): self.f = f; self.args = args
    def __repr__(self): return f"({self.f} {' '.join(str(a) for a in self.args)})"
class CPrim:
    def __init__(self, op, l, r, k): self.op = op; self.l = l; self.r = r; self.k = k
    def __repr__(self): return f"(let t = {self.l} {self.op} {self.r} in {self.k} t)"
class CIfZ:
    def __init__(self, c, t, e): self.c = c; self.t = t; self.e = e
    def __repr__(self): return f"(if0 {self.c} {self.t} {self.e})"

class CPSTransformer:
    def __init__(self):
        self.counter = 0
    def fresh(self, prefix="k"):
        self.counter += 1
        return f"{prefix}{self.counter}"

    def transform(self, expr, k):
        """Transform expr in CPS, passing result to continuation k."""
        if isinstance(expr, Var):
            return CApp(k, [expr])
        elif isinstance(expr, Num):
            return CApp(k, [expr])
        elif isinstance(expr, Lam):
            kp = self.fresh("k")
            body_cps = self.transform(expr.b, Var(kp))
            return CApp(k, [CLam([expr.p, kp], body_cps)])
        elif isinstance(expr, App):
            f_name = self.fresh("f")
            a_name = self.fresh("a")
            r_name = self.fresh("r")
            inner = CApp(Var(f_name), [Var(a_name), CLam([r_name], CApp(k, [Var(r_name)]))])
            a_cps = self.transform(expr.a, CLam([a_name], inner))
            return self.transform(expr.f, CLam([f_name], a_cps))
        elif isinstance(expr, BinOp):
            l_name = self.fresh("l")
            r_name = self.fresh("r")
            t_name = self.fresh("t")
            prim = CLam([t_name], CApp(k, [Var(t_name)]))
            inner = CPrim(expr.op, Var(l_name), Var(r_name), prim)
            r_cps = self.transform(expr.r, CLam([r_name], inner))
            return self.transform(expr.l, CLam([l_name], r_cps))
        elif isinstance(expr, IfZ):
            j = self.fresh("j")
            v = self.fresh("v")
            jlam = CLam([v], CApp(k, [Var(v)]))
            t_cps = self.transform(expr.t, Var(j))
            e_cps = self.transform(expr.e, Var(j))
            c_name = self.fresh("c")
            body = CApp(CLam([j], CIfZ(Var(c_name), CLam([], t_cps), CLam([], e_cps))), [jlam])
            return self.transform(expr.c, CLam([c_name], body))
        raise ValueError(f"Unknown: {expr}")

def main():
    print("=== CPS Transformation Demo ===\n")
    # fact = λn. if0 n 1 (n * fact(n-1))  — simplified
    # Simple: (λx. x + 1) 5
    e1 = App(Lam("x", BinOp("+", Var("x"), Num(1))), Num(5))
    print(f"Direct:  {e1}")
    cps = CPSTransformer()
    halt = Var("halt")
    c1 = cps.transform(e1, halt)
    print(f"CPS:     {c1}\n")

    # (λf. λx. f x) (λy. y + 1) 3
    e2 = App(App(Lam("f", Lam("x", App(Var("f"), Var("x")))),
                 Lam("y", BinOp("+", Var("y"), Num(1)))), Num(3))
    print(f"Direct:  {e2}")
    cps2 = CPSTransformer()
    c2 = cps2.transform(e2, halt)
    print(f"CPS:     {c2}\n")

    # if0 0 42 99
    e3 = IfZ(Num(0), Num(42), Num(99))
    print(f"Direct:  {e3}")
    cps3 = CPSTransformer()
    c3 = cps3.transform(e3, halt)
    print(f"CPS:     {c3}")

if __name__ == "__main__":
    main()

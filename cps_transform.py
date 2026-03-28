#!/usr/bin/env python3
"""Continuation-passing style (CPS) transformation."""
_k=[0]
def fresh(): _k[0]+=1;return f"k{_k[0]}"
def cps(expr,k="halt"):
    if isinstance(expr,(int,float,str)):
        return ("call",k,expr)
    if isinstance(expr,tuple):
        op=expr[0]
        if op=="let":
            _,var,val,body=expr
            k2=fresh()
            return cps(val,("lambda",[var],cps(body,k)))
        if op in "+-*/":
            a,b=expr[1],expr[2]
            ka=fresh();kb=fresh()
            return cps(a,("lambda",[ka],cps(b,("lambda",[kb],("call",k,(op,ka,kb))))))
        if op=="if":
            _,cond,then_e,else_e=expr
            kc=fresh()
            return cps(cond,("lambda",[kc],("if",kc,cps(then_e,k),cps(else_e,k))))
        if op=="call":
            fn,arg=expr[1],expr[2]
            kf=fresh();ka=fresh()
            return cps(fn,("lambda",[kf],cps(arg,("lambda",[ka],("call",kf,ka,k)))))
    return ("call",k,expr)
def to_str(expr,depth=0):
    if isinstance(expr,(int,float,str)): return str(expr)
    if isinstance(expr,tuple):
        if expr[0]=="lambda": return f"(λ{expr[1]}. {to_str(expr[2])})"
        if expr[0]=="call": return f"({' '.join(to_str(e) for e in expr[1:])})"
        if expr[0]=="if": return f"(if {to_str(expr[1])} {to_str(expr[2])} {to_str(expr[3])})"
        return f"({expr[0]} {' '.join(to_str(e) for e in expr[1:])})"
    return str(expr)
if __name__=="__main__":
    expr=("+",1,2)
    result=cps(expr);print(f"CPS of (+ 1 2): {to_str(result)}")
    expr2=("let","x",5,("+","x",3))
    result2=cps(expr2);print(f"CPS of let x=5 in x+3: {to_str(result2)}")
    print("CPS transform OK")

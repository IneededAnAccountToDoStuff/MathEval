# MathEval
It's a safe math parser for Python &amp; Javascript. Nothing more.
It parses math expressions, without the danger of stuff like `eval`. It supports functions, constants… [(listed below)](#features--usage)

## How can it be safe?
The engine does not rely on `eval` functionality at all. It is a custom parser.

### Warning
While the parser itself is safe and completely immune to attacks, the constants and functions you provide may not be. If you give a function that is unsafe, (e.g. 
```python
def unsafefunc(a:str):import os;os.system(a)
```
), then a malicious "math string" could call that function. Same with constants that are classes with dangerous methods.

## How to use
Download the language file, import it.

## Features & Usage
The language supports custom functions and constants. It natively handles basic arithmetic, as well as modulo, factorial, [derangement](https://en.wikipedia.org/wiki/Derangement), exponents, negation, unary plus, [multi-factorial](https://en.wikipedia.org/wiki/Double_factorial#Generalizations), comparators, ceiling & floor brackets.

For multiplication, `*` and `⋅` can be used.
For division, `÷` and `/` can be used.
For modulo, `mod` and `%` can be used.
For exponentiation, `^` and `**` can be used.

Comparators return their truthy values, and can be used with `<=`, `>=`, `=`, `!=`, `≥`, `≤`, `≠`, `=`, `>`, `<`.

### Demo
```python
import MathEval as me
assert me.calculate("5!+12")==120+12#Is true
assert me.calculate("pie+12",constants={'pie':3})==15#Using a constant
assert me.calculate("abs(-4)")==4#Function call
assert me.calculate("myfunc(-4)",funcs={"myfunc":abs})==4#Custom function
assert me.calculate("⌊2.8⌋+⌈2.1⌉+2*(3+2)")==15#Brackets
print(me._evaluate(me._tokenize("4+12*3")))#Internal function for parsing math, then executing
sympymode()#if you have sympy installed, it uses it. Otherwise it crashes.
calc_disp('12+4')#auto prints value

```
`calc_proc` and `calc_verbose` are debug functions. `_mathify` is an internal thingy.

## Language Choices
The order of operations was nonstandard outside of basic arithmetic. I tried to pick one that made some amout of sense.

## Efficiency
Questionable. Please raise a bug report if you have ideas for improvement.

## The JS Port
The JS (Javascript) port. It's buggy. The translation wasn't perfect. Also, the Python code is the way it is cause of Python's `RecursionError`. JS doesn't have that, so it's really unnecessary. I just needed it to work.


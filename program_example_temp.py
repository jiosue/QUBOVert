from qubovert import *
from qubovert.utils import *
from qubovert.problems import *
from qubovert.sat import *
from qubovert.program import *
from sympy import Symbol
#from numpy import *
from numpy.testing import *


program = """
var binary x
var binary y
var binary z
var int3 i

if x:
    enforce(not y, lam=5)
    enforce(i > 2, lam=6)
if not x and y:
    enforce(i == 3, 2)
if i == 4:
    enforce(x and y, 10)
if i == 0:
    enforce(z, 2)

minimize(i)
"""

comiled_program = compile_program(program)

# vars
x, y, z = binary_var('x'), binary_var('y'), binary_var('z')
i = integer_var('i', 3)

program = HOBO()

# if x:
# 	assert(not y, 5)
# 	assert(i > 2, 6)
program.add_constraint_NOT(y, lam=5*x)
program.add_constraint_gt_zero(i - 2, lam=6*x)

# if not x and y:
# 	assert(i == 3, 2)
program.add_constraint_eq_zero(i - 3, lam=2*AND(NOT(x), y))

# if i == 4:
# 	assert(x and y, 10)
# program.add_constraint_AND(x, y, lam=10*(something that is 0 if i != 4 otherwise is positive))
neq = (i - 4 + (2*binary_var('c') - 1)*(1+integer_var('b', 3)))**2
program.add_constraint_AND(x, y, lam=10*neq)

# if i == 0:
	# assert(y, 2)
neq = (i + (2*binary_var('e') - 1)*(1+integer_var('d', 3)))**2
program.add_constraint_ONE(z, lam=2*neq)

# minimize(i)
program += i


print(program.num_binary_variables)

possible_sols = set()

pubo = program.to_pubo()
for sol in pubo.solve_bruteforce(True):
	s = program.convert_solution(sol)
	possible_sols.add((
		x.value(s), y.value(s), z.value(s), i.value(s)
	))
print(possible_sols)

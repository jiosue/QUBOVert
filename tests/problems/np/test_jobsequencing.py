#   Copyright 2020 Joseph T. Iosue
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Contains tests for the JobSequencing class.
"""

from qubovert.problems import JobSequencing
from qubovert.utils import (
    solve_qubo_bruteforce, solve_quso_bruteforce,
    solve_pubo_bruteforce, solve_puso_bruteforce
)
from numpy import allclose


job_lengths = {"job1": 2, "job2": 3, "job3": 1}
num_workers = 2
problem = JobSequencing(job_lengths, num_workers, log_trick=False)
problem_log = JobSequencing(job_lengths, num_workers)
Q = problem.to_qubo()
Q_log = problem_log.to_qubo()
L = problem.to_quso()
L_log = problem_log.to_quso()
P = problem.to_pubo()
H = problem.to_puso()

solutions = ({'job1', 'job3'}, {'job2'}), ({'job2'}, {'job1', 'job3'})
obj_val = 3


def test_jobsequencing_str():

    assert eval(str(problem)) == problem
    assert eval(str(problem_log)) == problem_log


def test_jobsequencing_properties():

    x, m = (2, 1, 2), 2
    p = JobSequencing(x, m)
    assert p.job_lengths == x
    assert p.num_workers == m
    assert p.log_trick
    p.M

    x, m = dict(enumerate((2, 1, 2))), 2
    p = JobSequencing(x, m)
    assert p.job_lengths == x


def test_jobsequencing_bruteforce():

    assert problem.solve_bruteforce() in solutions
    assert (
        problem.solve_bruteforce(all_solutions=True) in
        (list(solutions), list(reversed(solutions)))
    )


def test_jobsequencing_bruteforce_solve():

    assert problem.solve_bruteforce() in solutions
    assert problem.solve_bruteforce(True) in (
        list(solutions), [solutions[1], solutions[0]]
    )


# QUBO

def test_jobsequencing_qubo_logtrick_solve():

    e, sol = solve_qubo_bruteforce(Q_log)
    solution = problem_log.convert_solution(sol)
    assert problem_log.is_solution_valid(solution)
    assert problem_log.is_solution_valid(sol)
    assert solution in solutions
    assert allclose(e, obj_val)

    e, sol = solve_qubo_bruteforce(problem_log.to_qubo(3))
    solution = problem_log.convert_solution(sol)
    assert problem_log.is_solution_valid(solution)
    assert problem_log.is_solution_valid(sol)
    assert solution in solutions
    assert allclose(e, obj_val)


def test_jobsequencing_qubo_solve():

    e, sol = solve_qubo_bruteforce(Q)
    solution = problem.convert_solution(sol)
    assert problem.is_solution_valid(solution)
    assert problem.is_solution_valid(sol)
    assert solution in solutions
    assert allclose(e, obj_val)


def test_jobsequencing_qubo_logtrick_numvars():

    assert (
        len(set(y for x in Q_log for y in x)) ==
        problem_log.num_binary_variables ==
        Q_log.num_binary_variables
    )


def test_jobsequencing_qubo_numvars():

    assert (
        len(set(y for x in Q for y in x)) ==
        problem.num_binary_variables ==
        Q.num_binary_variables
    )


# quso

def test_jobsequencing_quso_logtrick_solve():

    e, sol = solve_quso_bruteforce(L_log)
    solution = problem_log.convert_solution(sol)
    assert problem_log.is_solution_valid(solution)
    assert problem_log.is_solution_valid(sol)
    assert solution in solutions
    assert allclose(e, obj_val)


def test_jobsequencing_quso_solve():

    e, sol = solve_quso_bruteforce(L)
    solution = problem.convert_solution(sol)
    assert problem.is_solution_valid(solution)
    assert problem.is_solution_valid(sol)
    assert solution in solutions
    assert allclose(e, obj_val)


def test_jobsequencing_quso_logtrick_numvars():

    assert L_log.num_binary_variables == problem_log.num_binary_variables


def test_jobsequencing_quso_numvars():

    assert L.num_binary_variables == problem.num_binary_variables


# PUBO

def test_jobsequencing_pubo_solve():

    e, sol = solve_pubo_bruteforce(P)
    solution = problem.convert_solution(sol)
    assert problem.is_solution_valid(solution)
    assert problem.is_solution_valid(sol)
    assert solution in solutions
    assert allclose(e, obj_val)


# puso

def test_jobsequencing_puso_solve():

    e, sol = solve_puso_bruteforce(H)
    solution = problem.convert_solution(sol)
    assert problem.is_solution_valid(solution)
    assert problem.is_solution_valid(sol)
    assert solution in solutions
    assert allclose(e, obj_val)

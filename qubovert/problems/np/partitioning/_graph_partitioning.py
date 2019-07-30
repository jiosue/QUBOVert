#   Copyright 2019 Joseph T. Iosue
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
Contains the GraphPartitioning class. See `help(qubovert.GraphPartitioning)`.
"""

from qubovert.utils import Problem, IsingCoupling, IsingField


class GraphPartitioning(Problem):

    """
    Class to manage converting Graph Partitioning to and from its QUBO and
    Ising formluations. Based on the paper hereforth designated [Lucas]:
    [Andrew Lucas. Ising formulations of many np problems. Frontiers in
    Physics, 2:5, 2014.]

    The goal of the Graph Partitioning problem is to partition the verticies
    of a graph into two equal subsets such that the number of edges connecting
    the two subsets is minimized. There must be an even number of vertices.

    GraphPartitioning inherits some methods and attributes from the Problem
    class. See ``help(qubovert.utils.Problem)``.

    Example usage
    -------------
    >>> from qubovert import GraphPartitioning
    >>> from any_module import qubo_solver
    >>> # or you can use my bruteforce solver...
    >>> # from qubovert.utils import solve_qubo_bruteforce as qubo_solver
    >>> edges = {("a", "b"), ("a", "c"), ("c", "d"),
                 ("b", "c"), ("e", "f"), ("d", "e")}
    >>> problem = GraphPartitioning(edges)
    >>> Q, offset = problem.to_qubo()
    >>> obj, sol = qubo_solver(Q)
    >>> obj += offset
    >>> solution = problem.convert_solution(sol)

    >>> print(solution)
    ({'a', 'b', 'c'}, {'d', 'e', 'f'})

    >>> print(problem.is_solution_valid(solution))
    True

    This is True since the number of vertices in the first partition is equal
    to the number of vertices in the second partition.

    >>> print(obj)
    1

    This is 1 because there is 1 edge connecting the partitions.
    """

    def __init__(self, edges):
        """
        The goal of the Graph Partitioning problem is to partition the vertices
        of a graph into two equal subsets such that the number of edges
        connecting the two subsets is minimized. All naming conventions follow
        the names in the paper [Lucas].

        Parameters
        ----------
        edges : set of two element tuples.
            Describes edges of the graph. Important: the graph must have an
            even number of vertices!

        Examples
        -------
        >>> edges = {("a", "b"), ("a", "c")}
        >>> problem = GraphPartitioning(edges)

        >>> edges = {(0, 1), (0, 2)}
        >>> problem = GraphPartitioning(edges)
        """
        self._edges = edges.copy()
        self._vertices = {y for x in edges for y in x}
        self._vertex_to_index = {x: i for i, x in enumerate(self._vertices)}
        self._index_to_vertex = {i: x for x, i in
                                 self._vertex_to_index.items()}
        self._N, self._n = len(self._vertices), len(self._edges)
        if self._N % 2:
            raise ValueError("The graph must have an even number of vertices")

        all_degs = {}
        for e in edges:
            for q in e:
                all_degs[q] = all_degs.setdefault(q, 0) + 1
        self._degree = max(all_degs.values()) if all_degs else 0

    @property
    def E(self):
        """
        A copy of the set of edges of the graph. Updating the copy will not
        update the instance set.

        Returns
        -------
        E : set of two element tuples.
            A copy of the edge set defining the Graph Partitioning problem.
        """
        return self._edges.copy()

    @property
    def V(self):
        """
        A copy of the vertex set of the graph. Updating the copy will not
        update the instance set.

        Returns
        -------
        V : set.
            A copy of the set of vertices corresponding to the edge set for the
            Graph Partitioning problem.
        """
        return self._vertices.copy()

    @property
    def degree(self):
        """
        The maximum degree of the graph.

        Returns
        -------
        deg : int.
            A copy of the variable of the maximal degree of the graph.
        """
        return self._degree

    @property
    def num_binary_variables(self):
        """
        The number of binary variables that the QUBO and Ising use.

        Returns
        -------
        num : integer.
            The number of variables in the QUBO/Ising formulation.
        """
        return self._N

    def to_ising(self, A=None, B=1):
        """
        Create and return the graph partitioning problem in Ising form
        following section 2.2 of [Lucas]. The J coupling matrix for the Ising
        will be returned as an uppertriangular dictionary. Thus, the problem
        becomes minimizing
            sum_{i <= j} z[i] z[j] J[(i, j)] + sum_{i} z[i] h[i] + offset.
        A and B are parameters to enforce constraints.

        Parameters
        ----------
        A: positive float (optional, defaults to None).
            A enforces the constraints. If it is None, then A will be chosen
            to enforce hard constraints (equation 10 in [Lucas]). Note that
            this may not be optimal for a solver, often hard constraints result
            in unsmooth energy landscapes that are difficult to minimize. Thus
            it may be useful to play around with the magnitude of this value.
        B: positive float (optional, defaults to 1).
            Constant in front of the objective function to minimize. See
            section 2.2 of [Lucas].

        Returns
        -------
        res : tuple (h, J, offset).
            h : qubovert.utils.IsingField object.
                Maps variable labels to the Ising field value. For most
                practical purposes, you can use IsingField in the same
                way as an ordinary dictionary. For more information, see
                ``help(qubovert.utils.IsingField)``.
            J : qubovert.utils.IsingField object.
                J is the upper triangular Ising coupling matrix, a
                IsingCoupling object. For most practical purposes, you can use
                IsingCoupling in the same way as an ordinary dictionary. For
                more information, see ``help(qubovert.utils.IsingCoupling)``.
            offset : float.
                The part of the Ising function independent of variables. It is
                the value such that the solution to the Ising formulation is
                equal to the the total number of edges connecting the two
                partitions.

        Example
        --------
        >>> problem = GraphPartitioning({(0, 1), (1, 2), (0, 3)})
        >>> h, J, offset = problem.to_ising()
        """
        # all naming conventions follow the paper listed in the docstring
        if A is None:
            A = min(2*self._degree, self._N) * B / 8

        h, J = IsingField(), IsingCoupling()
        offset = A * self._N + B * self._n / 2

        # encode H_A (equation 8)
        for i in range(self._N):
            for j in range(i+1, self._N):
                J[(i, j)] += 2 * A

        # encode H_B (equation 9)
        for u, v in self._edges:
            J[(self._vertex_to_index[u], self._vertex_to_index[v])] -= B / 2

        return h, J, offset

    def convert_solution(self, solution):
        """
        Convert the solution to the QUBO or Ising to the solution to the
        Graph Partitioning problem.

        Parameters
        ----------
        solution : iterable or dict.
            The QUBO or Ising solution output. The QUBO solution output
            is either a list or tuple where indices specify the label of the
            variable and the element specifies whether it's 0 or 1 for QUBO
            (or -1 or 1 for Ising), or it can be a dictionary that maps the
            label of the variable to is value.

        Returns
        -------
        res: tuple of sets (partition1, partition2).
            partition1 : set.
                The first partition of verticies.
            partition2 : set.
                The second partition.

        Example
        -------
        >>> edges = {("a", "b"), ("a", "c"), ("c", "d"),
                     ("b", "c"), ("e", "f"), ("d", "e")}
        >>> problem = GraphPartitioning(edges)
        >>> Q, offset = problem.to_qubo()
        >>> obj, sol = solve_qubo(Q)
        >>> obj += offset
        >>> print(problem.convert_solution(sol))
        ({'a', 'b', 'c'}, {'d', 'e', 'f'})
        """
        if not isinstance(solution, dict):
            solution = dict(enumerate(solution))

        partition1 = set(
            self._index_to_vertex[i] for i, v in solution.items() if v == 1
        )
        partition2 = set(
            self._index_to_vertex[i] for i, v in solution.items() if v != 1
        )
        return partition1, partition2

    def is_solution_valid(self, solution):
        """
        Returns whether or not the proposed solution has an equal number of
        vertices in each partition.

        Parameters
        ----------
        solution : iterable or dict.
            solution can be the output of GraphPartitioning.convert_solution,
            or the  QUBO or Ising solver output. The QUBO solution output
            is either a list or tuple where indices specify the label of the
            variable and the element specifies whether it's 0 or 1 for QUBO
            (or -1 or 1 for Ising), or it can be a dictionary that maps the
            label of the variable to is value.

        Returns
        -------
        valid : boolean.
            True if the proposed solution is valid, else False.
        """
        not_converted = (
            not isinstance(solution, tuple) or len(solution) != 2 or
            not isinstance(solution[0], set) or
            not isinstance(solution[1], set)
        )

        if not_converted:
            solution = self.convert_solution(solution)

        return len(solution[0]) == len(solution[1])
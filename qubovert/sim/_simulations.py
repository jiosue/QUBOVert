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

"""_simulations.py.

This file contains the ``SpinSimulation`` and ``BooleanSimulation`` objects
which deal with using a Metropolis algorithm to simulate spin and boolean
models.

"""

from qubovert.utils import (
    puso_value, boolean_to_spin, spin_to_boolean, pubo_to_puso
)
import random
from numpy import exp


__all__ = 'SpinSimulation', 'BooleanSimulation'


class SpinSimulation:
    """SpinSimulation.

    ``SpinSimulation`` uses a Metropolis algorithm to simulate a spin system.
    The spin system can be "updated" at a temperature ``T``. Thus, we can get
    an idea of the time evolution of a spin system by creating a temperature
    schedule and seeing how the system evolves.

    Examples
    --------
    Consider the example of the ferromagnetic chain.

    >>> import qubovert as qv
    >>>
    >>> length = 50
    >>> spin_system = sum(
    >>>     -qv.spin_var(i) * qv.spin_var(i+1) for i in range(length)
    >>> )
    >>>
    >>> # initial state is all spin down
    >>> initial_state = {i: -1 for i in range(length)}
    >>> sim = qv.sim.SpinSimulation(spin_system, initial_state)
    >>>
    >>> # define a schedule. here we simulate at temperature 4 for 25 time
    >>> # steps, then temperature 2 for 25 time steps, then temperature 1 for
    >>> # 10 time steps.
    >>> schedule = (4, 25), (2, 25), (1, 10)
    >>> sim.schedule_update(schedule)
    >>>
    >>> print("final state", sim.state)
    >>> print("last 30 states", sim.get_past_states(30))

    See Also
    --------
    ``qv.sim.BooleanSimulation``.

    """

    def __init__(self, model, initial_state=None, memory=0):
        """__init__.

        Parameters
        ----------
        model : dict or type in ``qubovert.SPIN_MODELS``.
            The model to simulate. This should map tuples of spin variable
            labels to their respective coefficient in the Hamiltonian. For more
            information, see the docstrings for any of the models in
            ``qubovert.SPIN_MODELS``.
        initial_state : dict (optional, defaults to None).
            The initial state to start the simulation in. ``initial_state``
            should map spin label names to their initial values, where each
            value is either 1 or -1. If ``initial_state`` is None, then it
            will be initialized to all 1s.
        memory : int >= 0 (optional, defaults to 0).
            During the simulation, we keep a list of the most recent ``memory``
            states that the simulation was in. These can be accessed with
            ``self.get_past_states(number_of_states)``.

        """
        # if model is a Matrix object or PUSO, etc,
        # then variables will be defined.
        # variables must be a list so it can be used with random.choices in
        # the update method.
        try:
            self._variables = list(model.variables)
        except AttributeError:
            if isinstance(initial_state, dict):
                self._variables = list(initial_state.keys())
            else:
                self._variables = list({v for k in model for v in k})

        self._initial_state = (
            initial_state.copy() if initial_state is not None else
            {v: 1 for v in self._variables}
        )
        self.set_state(self._initial_state)

        # keep track of the most recent states
        self._past_states = []
        # how many previous states to remember
        self._memory = memory

        # create a dictionary mapping each bit to the graph that it affects.
        self._subgraphs = {v: {} for v in self._variables}
        for k, c in model.items():
            for v in k:
                self._subgraphs[v][k] = c

    def __str__(self):
        """__str__.

        Return
        ------
        s : str.

        """
        return self.__class__.__name__ + "(memory=%d)" % self._memory

    @property
    def memory(self):
        """memory.

        Returns
        -------
        memory : int >= 0 (optional, defaults to 0).
            During the simulation, we keep a list of the most recent ``memory``
            states that the simulation was in. These can be accessed with
            ``self.get_past_states(number_of_states)``.

        """
        return self._memory

    @property
    def state(self):
        """state.

        A copy of the current state of the system.

        Returns
        -------
        state : dict.
            Dictionary that maps spin labels to their values in {1, -1}.

        """
        return self._state.copy()

    @property
    def initial_state(self):
        """initial_state.

        A copy of the initial state of the system.

        Returns
        -------
        initial_state : dict.
            Dictionary that maps binary labels to their values.

        """
        return self._initial_state.copy()

    def set_state(self, state):
        """set_state.

        Set the state of the spin system to ``state``.

        Parameters
        ----------
        state : dict or iterable.
            ``state`` maps the spin variable labels to their corresponding
            values. In other words ``state[v]`` is the value of variable ``v``.
            A value must be either 1 or -1.

        """
        self._state = {v: state[v] for v in self._variables}
        if any(v not in {1, -1} for v in self._state.values()):
            raise ValueError("State must contain only 1's and -1's")

    def reset(self):
        """reset.

        Reset the simulation back to its original state.

        """
        self._past_states = []
        self.set_state(self._initial_state)

    def get_past_states(self, num_states=None):
        """get_past_states.

        Return the previous ``num_states`` states of the system (if that many
        exist; ``self`` only stores up the previous ``self.memory`` states).

        Parameters
        ----------
        num_states : int (optional, defaults to None).
            The number of previous update steps to include. If ``num_states``
            is None, then all the previous states in memory will be returned.

        Returns
        -------
        states : list of dicts.
            Each dict maps binary labels to their values.

        """
        if num_states == 1:
            return [self.state]
        elif num_states is None:
            num_states = self._memory
        return [
            s.copy() for s in self._past_states[-num_states+1:]
        ] + [self.state]

    def _add_past_state(self):
        """_add_past_state.

        Add the current state to the ``past_states`` memory. If there is no
        more memory left (see ``self.memory``) then remove the oldest state.

        Parameters
        ----------
        state : dict.
            Maps binary labels to their values.

        """
        if self._memory:
            self._past_states.append(self.state)
            if len(self._past_states) > self._memory:
                self._past_states.pop(0)

    def _flip_bit(self, label):
        """_flip_bit.

        Flip the spin labeled by ``label`` in the internal state.

        Parameters
        ----------
        label : hashable object.
            The label of the spin to flip.

        """
        self._state[label] *= -1

    def schedule_update(self, schedule, seed=None):
        """schedule_update.

        Update the simulation with a schedule.

        Parameters
        ----------
        schedule : iterable of tuples.
            Each element in ``schedule`` is a pair ``(T, n)`` which designates
            a temperature and a number of updates. See `Notes` below.
        seed : number (optional, defaults to None).
            The number to seed ``random`` with. If ``seed is None``, then
            ``random.seed`` will not be called.

        Notes
        -----
        The following two code blocks perform exactly the same thing.

        >>> sim = SpinSimulation(10)
        >>> for T in (3, 2):
        >>>     sim.update(T, 100)
        >>> sim.update(1, 50)

        >>> sim = SpinSimulation(10)
        >>> schedule = (3, 100), (2, 100), (1, 50)
        >>> sim.schedule_update(schedule)

        """
        if seed is not None:
            random.seed(seed)
        for T, n in schedule:
            self.update(T, n)

    def update(self, T, num_updates=1, seed=None):
        """update.

        Update the simulation at temperature ``T``. Updates the internal state.

        Parameters
        ----------
        T : number >= 0.
            Temperature.
        num_updates : int >= 1 (optional, defaults to 1).
            The number of times to update the simulation at the temperature.
        seed : number (optional, defaults to None).
            The number to seed ``random`` with. If ``seed is None``, then
            ``random.seed`` will not be called.

        """
        if seed is not None:
            random.seed(seed)

        if num_updates < 0:
            raise ValueError("Cannot update a negative number of times")
        elif num_updates > 1:
            for _ in range(num_updates):
                self.update(T)
        elif num_updates == 1:
            self._add_past_state()

            # for i in self._variables:  # dwave does this, why?

            # sample without replacement
            # for i in random.sample(self._variables, len(self._variables)):

            # sample with replacement. this is more valid because it results in
            # a totally memoryless simulation
            for i in random.choices(self._variables, k=len(self._variables)):
                # the change in energy from flipping variable i is equal to
                # -2 * (the energy of the subgraph depending on i)
                dE = -2 * puso_value(self._state, self._subgraphs[i])
                if dE <= 0 or (T and random.random() < exp(-dE / T)):
                    self._flip_bit(i)


class BooleanSimulation(SpinSimulation):
    """BooleanSimulation.

    ``BooleanSimulation`` uses a Metropolis algorithm to simulate a boolean
    system. The boolean system can be "updated" at a temperature ``T``. Thus,
    we can get an idea of the time evolution of a boolean system by creating a
    temperature schedule and seeing how the system evolves.

    ``BooleanSimulation`` inherits from ``SpinSimulation``. In fact,
    ``BooleanSimulation`` just deals internally with converting to and from
    a spin system; all the simulation is done with ``SpinSimulation``. See
    ``help(qubovert.sim.SpinSimulation)`` for more details.

    Examples
    --------
    Consider the following example where we minimize an objective function.

    >>> import qubovert as qv
    >>>
    >>> # create the objective function.
    >>> x = [qv.boolean_var(i) for i in range(10)]
    >>> model = sum(x)
    >>> model.add_constraint_le_zero(x[0] + x[2] - 3 * x[5] - 1, lam=3)
    >>>
    >>> # initial state is all variables equal to 1
    >>> initial_state = {i: 11 for i in range(length)}
    >>> sim = qv.sim.BooleanSimulation(model, initial_state)
    >>>
    >>> # define a schedule. here we simulate at temperature 4 for 25 time
    >>> # steps, then temperature 2 for 25 time steps, then temperature 1 for
    >>> # 10 time steps.
    >>> schedule = (4, 25), (2, 25), (1, 10)
    >>> sim.schedule_update(schedule)
    >>>
    >>> print("final state", sim.state)

    See Also
    --------
    ``qubovert.sim.SpinSimulation``.

    """

    def __init__(self, model, initial_state=None, memory=0):
        """__init__.

        Parameters
        ----------
        model : dict or type in ``qubovert.BOOLEAN_MODELS``.
            The model to simulate. This should map tuples of boolean variable
            labels to their respective coefficient in the objective function.
            For more information, see the docstrings for any of the models in
            ``qubovert.BOOLEAN_MODELS``.
        initial_state : dict (optional, defaults to None).
            The initial state to start the simulation in. ``initial_state``
            should map boolean label names to their initial values, where each
            value is either 0 or 1. If ``initial_state`` is None, then it
            will be initialized to all 0s.
        memory : int >= 0 (optional, defaults to 0).
            During the simulation, we keep a list of the most recent ``memory``
            states that the simulation was in. These can be accessed with
            ``self.get_past_states(number_of_states)``.

        """
        model = pubo_to_puso(model)
        if initial_state is None:
            initial_state = {v: 0 for v in model._variables}
        super().__init__(model, initial_state, memory)

    @property
    def state(self):
        """state.

        A copy of the current state of the system.

        Returns
        -------
        state : dict.
            Dictionary that maps boolean labels to their values in {0, 1}.

        """
        return spin_to_boolean(self._state)

    def set_state(self, state):
        """set_state.

        Set the state of the spin system to ``state``.

        Parameters
        ----------
        state : dict or iterable.
            ``state`` maps the spin variable labels to their corresponding
            values. In other words ``state[v]`` is the value of variable ``v``.
            A value must be either 0 or 1.

        """
        # if we call super then we get the wrong errors
        state = {v: state[v] for v in self._variables}
        if any(v not in {0, 1} for v in state.values()):
            raise ValueError("State must contain only 0's and 1's")
        self._state = boolean_to_spin(state)
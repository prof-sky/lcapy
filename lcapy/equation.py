"""This module provides the Equation class.

Copyright 2023 Michael Hayes, UCECE

"""

from .expr import ExprPrint, ExprMisc, expr
from sympy import Eq


class Equation(ExprPrint, ExprMisc):

    is_Equality = True

    def __init__(self, lhs, rhs):

        self.lhs = expr(lhs)
        self.rhs = expr(rhs)

    @property
    def _pexpr(self):
        """Return expression for printing."""

        # FIXME, If lhs == rhs, SymPy prints True
        return Eq(self.lhs.sympy, self.rhs.sympy)

    # TODO, perhaps add canonical, etc.

    def __call__(self, arg, **assumptions):
        """Transform domain."""

        from .transform import call

        return Equation(call(self.lhs, arg, **assumptions),
                        call(self.rhs, arg, **assumptions))

    @property
    def symbols(self):
        """Return dictionary of symbols in the equation keyed by name."""

        return self.lhs.symbols + self.rhs.symbols

"""This module provides the TimeDomainExpression class to represent time domain expressions.

Copyright 2014--2020 Michael Hayes, UCECE

"""

from __future__ import division
from .expr import Expr
from .functions import exp
from .sym import fsym, ssym, tsym, j, oo, tausym
from .acdc import is_dc, is_ac, is_causal
from .laplace import laplace_transform
from .fourier import fourier_transform
from .voltagemixin import VoltageMixin
from .currentmixin import CurrentMixin
from sympy import Heaviside, limit, Integral, Expr as symExpr


class TimeDomainExpression(Expr):
    """t-domain expression or symbol."""

    var = tsym
    domain = 'Time'
    domain_label = 'Time'
    domain_units = 's'
    is_time_domain = True

    def __init__(self, val, **assumptions):

        check = assumptions.pop('check', True)        
        assumptions['real'] = True
        super(TimeDomainExpression, self).__init__(val, **assumptions)

        expr = self.expr        
        if check and expr.find(ssym) != set() and not expr.has(Integral):
            raise ValueError(
                't-domain expression %s cannot depend on s' % expr)
        if check and expr.find(fsym) != set() and not expr.has(Integral):
            raise ValueError(
                't-domain expression %s cannot depend on f' % expr)

    def _mul_compatible(self, x):

        if x.is_constant_domain:
            return True
        if self.quantity is 'undefined' or x.quantity is 'undefined':
            return True
        
        # TODO: allow TimeDomainVoltage**2 one day.
        return False

    def _div_compatible(self, x):

        return x.is_constant_domain

    def _class_by_quantity(self, quantity):

        if quantity == 'voltage':
            return TimeDomainVoltage
        elif quantity == 'current':
            return TimeDomainCurrent
        elif quantity == 'impedance':
            return TimeDomainImpedance
        elif quantity == 'admittance':
            return TimeDomainAdmittance
        elif quantity == 'transfer':
            return TimeDomainImpulseResponse
        elif quantity == 'undefined':
            return TimeDomainExpression                                
        raise ValueError('Unknown quantity %s' % quantity)
    
    def as_expr(self):
        return TimeDomainExpression(self)

    def as_voltage(self):
        return TimeDomainVoltage(self)

    def as_current(self):
        return TimeDomainCurrent(self)    

    def as_impedance(self):
        return TimeDomainImpedance(self)

    def as_admittance(self):
        return TimeDomainAdmittance(self)

    def as_transfer(self):
        return TimeDomainImpulseResponse(self)    
    
    def infer_assumptions(self):

        self.assumptions['dc'] = False
        self.assumptions['ac'] = False
        self.assumptions['causal'] = False

        var = self.var
        if is_dc(self, var):
            self.assumptions['dc'] = True
            return

        if is_ac(self, var):
            self.assumptions['ac'] = True
            return

        if is_causal(self, var):
            self.assumptions['causal'] = True

    def laplace(self, evaluate=True, **assumptions):
        """Determine one-sided Laplace transform with 0- as the lower limit."""

        # The assumptions are required to help with the inverse Laplace
        # transform if required.
        self.infer_assumptions()

        assumptions = self.merge_assumptions(**assumptions)
        
        result = laplace_transform(self.expr, self.var, ssym, evaluate=evaluate)
        return self.wrap(LaplaceDomainExpression(result, **assumptions))

    def phasor(self, **assumptions):
        """Convert to phasor domain."""

        return PhasorDomainExpression.make(self, **assumptions)

    def LT(self, **assumptions):
        """Convert to s-domain.   This is an alias for laplace."""

        return self.laplace(**assumptions)
    
    def fourier(self, evaluate=True, **assumptions):
        """Attempt Fourier transform."""

        assumptions = self.merge_assumptions(**assumptions)
        
        result = fourier_transform(self.expr, self.var, fsym, evaluate=evaluate)
        return self.wrap(FourierDomainExpression(result, **assumptions))

    def angular_fourier(self, evaluate=True, **assumptions):
        """Attempt angular Fourier transform."""

        from .symbols import omega, pi, f

        result = self.fourier(evaluate, **assumptions).subs(f, omega / (2 * pi))
        # Could optimise...
        return self.wrap(AngularFourierDomainExpression(result, **assumptions))        

    def FT(self, **assumptions):
        """Convert to f-domain.   This is an alias for fourier."""

        return self.fourier(**assumptions)    

    def phasor(self, **assumptions):

        return PhasorDomainExpression.make(self, **assumptions)

    def time(self, **assumptions):
        return self

    def plot(self, t=None, **kwargs):
        """Plot the time waveform.  If t is not specified, it defaults to the
        range (-0.2, 2).  t can be a vector of specified instants, a
        tuple specifing the range, or a constant specifying the
        maximum value with the minimum value set to 0.

        kwargs include:
        axes - the plot axes to use otherwise a new figure is created
        xlabel - the x-axis label
        ylabel - the y-axis label
        xscale - the x-axis scaling, say for plotting as ms
        yscale - the y-axis scaling, say for plotting mV
        in addition to those supported by the matplotlib plot command.
        
        The plot axes are returned."""

        from .plot import plot_time
        return plot_time(self, t, **kwargs)

    def sample(self, t):

        """Return a discrete-time signal evaluated at time values specified by
        vector t. """

        return self.evaluate(t)

    def initial_value(self):
        """Determine value at t = 0. 
        See also pre_initial_value and post_initial_value"""

        return self.subs(0)

    def pre_initial_value(self):
        """Determine value at t = 0-.
        See also initial_value and post_initial_value"""

        return self.limit(self.var, 0, dir='-')

    def post_initial_value(self):
        """Determine value at t = 0+.
        See also pre_initial_value and initial_value"""

        return self.limit(self.var, 0, dir='+')    

    def final_value(self):
        """Determine value at t = oo."""

        return self.limit(self.var, oo)

    def remove_condition(self):
        """Remove the piecewise condition from the expression.
        See also force_causal."""

        if not self.is_conditional:
            return self
        expr = self.expr
        expr = expr.args[0].args[0]
        return self.__class__(expr)

    def force_causal(self):
        """Remove the piecewise condition from the expression
        and multiply by Heaviside function.  See also remove_condition."""

        if self.is_causal:
            return self
        
        expr = self.expr
        if self.is_conditional:
            expr = expr.args[0].args[0]            
        expr = expr * Heaviside(t)
        return self.__class__(expr)        

    def convolve(self, impulseresponse, commutate=False, **assumptions):
        """Convolve self with impulse response."""

        if not isinstance(impulseresponse, TimeDomainExpression):
            raise ValueError('Expecting TimeDomainExpression for impulse response')

        f1 = self.expr
        f2 = impulseresponse.expr
        if commutate:
            f1, f2 = f2, f1
        result = Integral(f1.subs(self.var, self.var - tausym) *
                          f2.subs(self.var, tausym),
                          (tausym, -oo, oo))
        return self.__class__(result, **assumptions)

    
class TimeDomainAdmittance(TimeDomainExpression):
    """t-domain 'admittance' value."""

    quantity = 'admittance'
    quantity_label = 'Admittance'
    units = 'siemens/s'
    is_impedance = True    


class TimeDomainImpedance(TimeDomainExpression):
    """t-domain 'impedance' value."""

    quantity = 'impedance'
    quantity_label = 'Impedance'
    units = 'ohms/s'
    is_impedance = True


class TimeDomainVoltage(VoltageMixin, TimeDomainExpression):
    """t-domain voltage (units V)."""
    pass

        
class TimeDomainCurrent(CurrentMixin, TimeDomainExpression):
    """t-domain current (units A)."""
    pass


class TimeDomainImpulseResponse(TimeDomainExpression):
    """impulse response"""

    # TODO, check attributes.
    quantity = 'transfer'
    quantity_label = 'Impulse response'
    units = '1/s'
    is_transfer = True


def texpr(arg, **assumptions):
    """Create TimeDomainExpression object.  If `arg` is tsym return t"""

    if arg is tsym:
        return t
    return TimeDomainExpression(arg, **assumptions)

from .sexpr import LaplaceDomainExpression
from .fexpr import FourierDomainExpression
from .omegaexpr import AngularFourierDomainExpression
from .cexpr import ConstantExpression
from .phasor import PhasorDomainExpression

t = TimeDomainExpression('t')
